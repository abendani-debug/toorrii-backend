from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import PolitiqueConfidentialite
from adminToorrii.serializers import (
    PolitiqueConfidentialiteAdminSerializer,
    PolitiqueConfidentialitePublicSerializer
)
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class AfficherPolitiqueDetailView(APIView):
    """
    GET /api/politique/
    Endpoint pour afficher un enregistrement de la table politique de confidentialité de l'entreprise par ID.
    Accessible par tous les utilisateurs.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Afficher la politique de confidentialité actuelle",
        description=(
            "Récupère la politique de confidentialité actuelle.\n\n"
            "Pour les utilisateurs authentifiés : renvoie toutes les informations (AdminSerializer).\n"
            "Pour le public : renvoie uniquement les champs accessibles publiquement (PublicSerializer)."
        ),
        responses={
            200: OpenApiResponse(
                description="Politique récupérée avec succès",
                response=PolitiqueConfidentialiteAdminSerializer(many=False),
                examples=[
                    OpenApiExample(
                        "Réponse admin 200",
                        value={
                            "politique_id": "POL_1",
                            "titre": {"fr": "Politique de confidentialité", "en": "Privacy Policy", "ar": "سياسة الخصوصية"},
                            "contenu": {"fr": "Contenu FR", "en": "Content EN", "ar": "المحتوى AR"},
                            "version": 1,
                            "active": True,
                            "date_creation": "2025-12-20T14:00:00Z",
                            "historique_modifications": ["Créé le 2025-12-20 14:00:00"]
                        }
                    ),
                    OpenApiExample(
                        "Réponse publique 200",
                        value={
                            "titre": {"fr": "Politique de confidentialité", "en": "Privacy Policy", "ar": "سياسة الخصوصية"},
                            "contenu": {"fr": "Contenu FR", "en": "Content EN", "ar": "المحتوى AR"},
                            "version": 1
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Aucune politique n'existe aved ce ID",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Aucune politique de confidentialité enregistrée."}
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
    def get(self, request, politique_id):
        try:
            politique = PolitiqueConfidentialite.objects.get(politique_id=politique_id)

            if not politique:
                return Response(
                    {"status": False, "message": "Aucune politique de confidentialité enregistrée aved ce ID."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = (
                PolitiqueConfidentialiteAdminSerializer(politique)
                if request.user.is_authenticated
                else PolitiqueConfidentialitePublicSerializer(politique)
            )

            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Erreur dans AfficherPolitiqueDetailView: %s", str(e))
            return Response({"status": False, "message": "Une erreur interne est survenue."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
