from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from adminToorrii.models import Utilisateur, AdminUser, Professionnel


@method_decorator(csrf_protect, name='dispatch')
class RefreshAccessTokenView(APIView):
    """
    Endpoint sécurisé pour rafraîchir le token JWT avec rotation et blacklist
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentication"],
        summary="Refresh Access Token (Secure)",
        description=(
            "Génère un nouvel access token à partir du refresh token stocké en cookie sécurisé.\n\n"
            " Sécurité implémentée :\n"
            "- Protection CSRF via Django\n"
            "- Refresh token en HttpOnly cookie\n"
            "- Vérification utilisateur en base\n"
            "- Vérification état du compte\n"
            "- Rotation du refresh token\n"
            "- Blacklist de l'ancien token\n\n"
            " Cookie requis :\n"
            "- refresh_token\n\n"
            " Header requis :\n"
            "- X-CSRFToken"
        ),
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Nouveau access token généré",
                examples=[
                    OpenApiExample(
                        name="Succès",
                        value={
                            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "email": "user@example.com",
                            "role": "admin"
                        },
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Token invalide ou manquant",
                examples=[
                    OpenApiExample(
                        name="Token manquant",
                        value={"error": "Refresh token manquant"},
                        response_only=True
                    ),
                    OpenApiExample(
                        name="Token invalide",
                        value={"error": "Refresh token invalide ou expiré"},
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        name="Compte désactivé",
                        value={"error": "Compte désactivé"},
                        response_only=True
                    ),
                    OpenApiExample(
                        name="CSRF invalide",
                        value={"detail": "CSRF Failed: CSRF token missing or incorrect."},
                        response_only=True
                    )
                ]
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Utilisateur introuvable",
                examples=[
                    OpenApiExample(
                        name="Utilisateur non trouvé",
                        value={"error": "Utilisateur introuvable"},
                        response_only=True
                    )
                ]
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        name="Blacklist non configurée",
                        value={"error": "Blacklist non configurée"},
                        response_only=True
                    )
                ]
            )
        },
        methods=["POST"]
    )
    def post(self, request):
        
        #  Vérification CSRF
        csrf_cookie = request.COOKIES.get("csrftoken")
        csrf_header = request.headers.get("X-CSRFToken")

        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return Response(
                {"error": "Invalid CSRF Token"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ==========================
        # 1. Récupération refresh token depuis cookie
        # ==========================
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token manquant"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ==========================
        # 2. Validation du token
        # ==========================
        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            #  Token invalide → supprimer le cookie
            response = Response(
                {"error": "Refresh token invalide ou expiré"},
                status=status.HTTP_401_UNAUTHORIZED
            )

            response.delete_cookie("refresh_token")
            return response


        # ==========================
        # 3. Extraction user_id
        # ==========================
        user_id = refresh.payload.get("user_id")

        if not user_id:
            return Response(
                {"error": "Token invalide"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ==========================
        # 4. Vérification utilisateur
        # ==========================
        try:
            utilisateur = Utilisateur.objects.get(pk=user_id)
        except Utilisateur.DoesNotExist:
            return Response(
                {"error": "Utilisateur introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not utilisateur.is_active:
            return Response(
                {"error": "Compte désactivé"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ==========================
        # 5. Détermination du rôle (optimisé)
        # ==========================
        admin = AdminUser.objects.filter(email=utilisateur.email).first()

        if admin:
            if admin.etat_compte != 'A':
                return Response({"error": "Compte admin inactif"}, status=403)
            role = "admin"
        else:
            pro = Professionnel.objects.filter(email=utilisateur.email).first()

            if pro:
                if pro.etat_compte != 'A':
                    return Response({"error": "Compte professionnel inactif"}, status=403)
                role = "professionnel"
            else:
                return Response(
                    {"error": "Rôle non reconnu"},
                    status=status.HTTP_403_FORBIDDEN
                )

        # ==========================
        # 6. Blacklist ancien refresh
        # ==========================
        try:
            refresh.blacklist()
        except AttributeError:
            return Response(
                {"error": "Blacklist non configurée"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ==========================
        # 7. Rotation refresh token
        # ==========================
        new_refresh = RefreshToken.for_user(utilisateur)

        # ==========================
        # 8. Génération access token
        # ==========================
        access = new_refresh.access_token
        access["email"] = utilisateur.email
        access["role"] = role

        # ==========================
        # 9. Réponse + cookie sécurisé
        # ==========================
        response = Response(
            {
                "access": str(access),
                "email": utilisateur.email,
                "role": role,
            },
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="refresh_token",
            value=str(new_refresh),
            httponly=True,
            secure=not settings.DEBUG,  # OK en dev et prod
            samesite="None" if not settings.DEBUG else "Lax",
            max_age=30 * 24 * 60 * 60
        )

        return response