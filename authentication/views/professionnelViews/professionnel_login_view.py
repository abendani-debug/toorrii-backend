from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.middleware.csrf import get_token, rotate_token
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from adminToorrii.models import Professionnel, Utilisateur
from authentication.utils.token import get_tokens_for_user_professionnel
from authentication.serializers import LoginProfessionnelSerializer, ProfessionnelLoginResponseSerializer


class ProfessionnelLoginView(APIView):
    """
    Endpoint de connexion pour les professionnels avec JWT et CSRF.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentification Professionnel"],
        summary="Connexion professionnel",
        description=(
            "Authentifie un professionnel et retourne un access token JWT.\n\n"
            " Sécurité :\n"
            "- CSRF Token requis (cookie + header)\n"
            "- Refresh token stocké dans un cookie HttpOnly\n\n"
            " Cookies retournés :\n"
            "- refresh_token (HttpOnly, Secure)\n"
            "- csrftoken (accessible côté frontend)"
        ),

        request=LoginProfessionnelSerializer,
        responses={
            200: OpenApiResponse(
                response=ProfessionnelLoginResponseSerializer,
                description="Connexion réussie"
            ),
            400: OpenApiResponse(description="Erreur de validation"),
            401: OpenApiResponse(description="Email ou mot de passe incorrect"),
            403: OpenApiResponse(description="Compte non autorisé ou CSRF invalide"),
            404: OpenApiResponse(description="Compte introuvable"),
        },

        examples=[
            OpenApiExample(
                "Exemple requête",
                summary="Login request",
                value={"email": "pro@test.com", "password": "Pro123!"},
                request_only=True
            ),
            OpenApiExample(
                "Connexion réussie",
                summary="Réponse succès",
                value={
                    "professionnel_id": "PRO123",
                    "email": "pro@test.com",
                    "nom": "Jean Dupont",
                    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                },
                response_only=True,
                status_codes=["200"]
            )
        ]
    )
    def post(self, request):
        # Vérification CSRF
        csrf_cookie = request.COOKIES.get("csrftoken")
        csrf_header = request.headers.get("X-CSRFToken")
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return Response({"error": "Invalid CSRF Token"}, status=status.HTTP_403_FORBIDDEN)

        # Validation données
        serializer = LoginProfessionnelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Vérifier existence du professionnel
        try:
            professionnel = Professionnel.objects.get(email=email)
        except Professionnel.DoesNotExist:
            return Response({"error": "Ce compte n'existe pas."}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier état du compte
        if professionnel.etat_compte != 'A':
            return Response({"error": "Ce compte n'est pas autorisé."}, status=status.HTTP_403_FORBIDDEN)

        # Authentification
        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({"error": "Email ou mot de passe incorrect."}, status=status.HTTP_401_UNAUTHORIZED)

        # Récupération utilisateur lié
        try:
            utilisateur = Utilisateur.objects.get(email=professionnel.email)
        except Utilisateur.DoesNotExist:
            return Response({"error": "Utilisateur lié introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Génération JWT
        tokens = get_tokens_for_user_professionnel(utilisateur)
        access_token = tokens["access"]
        refresh_token = tokens["refresh"]

        # Rotation CSRF
        rotate_token(request)
        new_csrf_token = get_token(request)

        # Réponse
        response = Response({
            "professionnel_id": professionnel.professionnel_id,
            "email": professionnel.email,
            "access": access_token
        }, status=status.HTTP_200_OK)

        # Cookie refresh token (HttpOnly)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=30*24*60*60
        )

        # Cookie CSRF
        response.set_cookie(
            key="csrftoken",
            value=new_csrf_token,
            httponly=False,
            secure=False,
            samesite='Strict',
        )

        return response