from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from authentication.serializers import LogoutResponseSerializer


class LogoutView(APIView):
    """
    Déconnexion utilisateur :
    - Vérifie le CSRF token.
    - Blackliste le refresh token.
    - Supprime le cookie refresh_token.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Authentification Admin"],
        summary="Déconnexion utilisateur",
        description=(
            "Révoque le refresh token de l'utilisateur connecté.\n\n"
            " Sécurité :\n"
            "- Vérification CSRF (cookie + header)\n"
            "- Blacklist du refresh token\n"
            "- Suppression du cookie refresh_token"
        ),

        responses={
            205: OpenApiResponse(
                response=LogoutResponseSerializer,
                description="Déconnexion réussie"
            ),
            400: OpenApiResponse(description="Refresh token manquant ou invalide"),
            403: OpenApiResponse(description="CSRF token invalide"),
            401: OpenApiResponse(description="Utilisateur non authentifié"),
        },

        examples=[
            #  SUCCESS
            OpenApiExample(
                name="Succès",
                value={"message": "Déconnexion réussie"},
                response_only=True,
                status_codes=["205"]
            ),

            #  400
            OpenApiExample(
                name="Refresh manquant",
                value={"error": "Refresh token manquant"},
                response_only=True,
                status_codes=["400"]
            ),

            OpenApiExample(
                name="Refresh invalide",
                value={"error": "Refresh token invalide ou expiré"},
                response_only=True,
                status_codes=["400"]
            ),

            #  403
            OpenApiExample(
                name="CSRF invalide",
                value={"error": "Invalid CSRF Token"},
                response_only=True,
                status_codes=["403"]
            ),

            #  401
            OpenApiExample(
                name="Non authentifié",
                value={"detail": "Authentication credentials were not provided."},
                response_only=True,
                status_codes=["401"]
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

        #  Récupération du refresh token
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"error": "Refresh token manquant"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Blacklist
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"error": "Refresh token invalide ou expiré"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Réponse
        response = Response(
            {"message": "Déconnexion réussie"},
            status=status.HTTP_205_RESET_CONTENT
        )

        #  Suppression cookie
        response.delete_cookie("refresh_token")

        return response