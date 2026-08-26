from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


class GetCSRFToken(APIView):

    permission_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Récupérer le token CSRF",
        description=(
            "Cet endpoint génère et retourne un token CSRF pour sécuriser les requêtes POST/PUT/DELETE.\n\n"
            "Utilisation :\n"
            "- Le frontend doit appeler cet endpoint avant toute authentification ou action sensible\n"
            "- Le token est stocké dans un cookie `csrftoken`\n\n"
            "Sécurité :\n"
            "- Cookie sécurisé (configurable via settings Django)\n"
            "- Utilisé pour la protection contre les attaques CSRF"
        ),

        responses={
            200: OpenApiResponse(
                description="Token CSRF généré avec succès"
            ),
        },

        examples=[
            OpenApiExample(
                "Réponse succès",
                value={
                    "detail": "CSRF cookie set"
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        csrf_token = get_token(request)

        response = Response(
            {"detail": "CSRF cookie set"},
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="csrftoken",
            value=csrf_token,
            secure=True,
            httponly=False,  # accessible JS
            samesite="Strict",
            max_age=30 * 24 * 60 * 60
        )

        return response