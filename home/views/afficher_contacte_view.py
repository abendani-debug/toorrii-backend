from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from adminToorrii.models import Contacte
from adminToorrii.serializers import ContacteAdminSerializer, ContactePublicSerializer
import logging

logger = logging.getLogger(__name__)

class AfficherContacteView(APIView):
    """
    GET /api/contact/
    Retourne les informations de contact de l’entreprise.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Obtenir les informations de contact",
        description=(
            "Retourne les informations de contact.\n\n"
            "- **Utilisateur authentifié** : toutes les informations (Admin)\n"
            "- **Utilisateur non authentifié (public)** : informations publiques uniquement\n\n"
            " Il ne peut y avoir qu’un seul enregistrement Contacte."
        ),
        responses={
            200: OpenApiResponse(
                description="Informations de contact récupérées avec succès",
                response=ContactePublicSerializer(many=False),
                examples=[
                    OpenApiExample(
                        "Réponse publique",
                        value={
                            "status": True,
                            "data": {
                                "email": "contact@toorrii.com",
                                "telephone_1": "+213600000000",
                                "telephone_2": "+213610000000",
                                "telephone_fixe": "021000000",
                                "adresse": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "ville": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "wilaya": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "horaires": "08:00 - 18:00",
                                "site_web": "https://toorrii.com",
                                "facebook": "https://facebook.com/toorrii",
                                "instagram": None,
                                "tiktok": None,
                                "linkedin": None,
                                "x": None,
                                "message_acceuil": {"fr": "Bienvenue", "en": "Welcome", "ar": "مرحبا"}
                            }
                        }
                    ),
                    OpenApiExample(
                        "Réponse admin",
                        value={
                            "status": True,
                            "data": {
                                "id": 1,
                                "email": "contact@toorrii.com",
                                "telephone_1": "+213600000000",
                                "telephone_2": "+213610000000",
                                "telephone_fixe": "021000000",
                                "adresse": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "ville": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "wilaya": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "horaires": "08:00 - 18:00",
                                "site_web": "https://toorrii.com",
                                "facebook": "https://facebook.com/toorrii",
                                "instagram": None,
                                "tiktok": None,
                                "linkedin": None,
                                "x": None,
                                "message_acceuil": {"fr": "Bienvenue", "en": "Welcome", "ar": "مرحبا"},
                                "date_creation": "2025-12-20T14:00:00Z",
                                "historique_modifications": []
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Aucun contact enregistré",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Aucun contact enregistré."}
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne du serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={"status": False, "message": "Une erreur interne est survenue."}
                    )
                ]
            ),
        }
    )
    def get(self, request):
        try:
            contact = Contacte.objects.first()

            if not contact:
                return Response(
                    {"status": False, "message": "Aucun contact enregistré."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer_class = (
                ContacteAdminSerializer if request.user.is_authenticated else ContactePublicSerializer
            )
            serializer = serializer_class(contact, many=False)

            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Erreur dans AfficherContacteView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
