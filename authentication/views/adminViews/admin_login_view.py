from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from authentication.serializers import LoginSerializer, AdminLoginResponseSerializer
from adminToorrii.models import AdminUser, Utilisateur
from authentication.utils.token import get_tokens_for_user_admin
from django.contrib.auth import authenticate


class AdminLoginView(APIView):
    """
    Endpoint de connexion pour les administrateurs avec JWT et CSRF.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentification Admin"],
        summary="Connexion administrateur",
        description=(
            "Authentifie un administrateur et retourne un access token JWT.\n\n"
            " Sécurité :\n"
            "- CSRF Token requis (cookie + header)\n"
            "- Refresh token stocké dans un cookie HttpOnly\n\n"
            " Cookies retournés :\n"
            "- refresh_token (HttpOnly, Secure)\n"
            "- csrftoken (accessible côté frontend)"
        ),

        request=LoginSerializer,

        responses={
            200: OpenApiResponse(
                response=AdminLoginResponseSerializer,
                description="Connexion réussie"
            ),
            400: OpenApiResponse(description="Erreur de validation"),
            401: OpenApiResponse(description="Email ou mot de passe incorrect"),
            403: OpenApiResponse(description="Compte non autorisé ou CSRF invalide"),
            404: OpenApiResponse(description="Compte introuvable"),
        },

        examples=[
            #  REQUEST
            OpenApiExample(
                name="Exemple requête",
                summary="Login request",
                value={
                    "email": "admin@test.com",
                    "password": "Admin123!"
                },
                request_only=True
            ),

            #  SUCCESS
            OpenApiExample(
                name="Connexion réussie",
                summary="Réponse succès",
                value={
                    "admin_id": "ADM123",
                    "email": "admin@test.com",
                    "nom": "John Doe",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                },
                response_only=True,
                status_codes=["200"]
            ),

            #  400
            OpenApiExample(
                name="Erreur validation",
                value={
                    "email": ["Ce champ est obligatoire."],
                    "password": ["Ce champ est obligatoire."]
                },
                response_only=True,
                status_codes=["400"]
            ),

            #  401
            OpenApiExample(
                name="Identifiants incorrects",
                value={
                    "error": "Email ou mot de passe incorrect."
                },
                response_only=True,
                status_codes=["401"]
            ),

            #  403
            OpenApiExample(
                name="CSRF invalide",
                value={
                    "error": "Invalid CSRF Token"
                },
                response_only=True,
                status_codes=["403"]
            ),

            #  404
            OpenApiExample(
                name="Compte introuvable",
                value={
                    "error": "Ce compte n'existe pas."
                },
                response_only=True,
                status_codes=["404"]
            ),
        ]
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

        #  Validation des données
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        #  Vérifier admin
        try:
            admin_user = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return Response(
                {"error": "Ce compte n'existe pas."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  Vérifier état du compte
        if admin_user.etat_compte != 'A':
            return Response(
                {"error": "Ce compte n'est pas autorisé."},
                status=status.HTTP_403_FORBIDDEN
            )

        #  Authentification
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"error": "Email ou mot de passe incorrect."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        #  Récupération utilisateur lié
        try:
            utilisateur = Utilisateur.objects.get(email=admin_user.email)
        except Utilisateur.DoesNotExist:
            return Response(
                {"error": "Utilisateur lié introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  Génération JWT
        tokens = get_tokens_for_user_admin(utilisateur)
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]

        #  Réponse
        response = Response({
            "admin_id": admin_user.admin_id,
            "email": admin_user.email,
            "nom": admin_user.nom,
            "access": access_token
        }, status=status.HTTP_200_OK)

        #  Cookie refresh token (HttpOnly)
        # SameSite=None : le frontend (Vercel) et le backend (Render) sont
        # sur des domaines différents, le cookie doit pouvoir circuler cross-site.
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='None',
            max_age=30*24*60*60
        )

        return response