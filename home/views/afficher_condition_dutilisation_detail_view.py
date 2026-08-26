from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import ConditionDutilisation
from adminToorrii.serializers import (
    ConditionDutilisationAdminSerializer,
    ConditionDutilisationPublicSerializer
)
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class AfficherConditionDutilisationDetailView(APIView):
    """
    Endpoint pour afficher une condition d`utilisation par ID.
    Accessible par tous les utilisateurs.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Afficher une condition d'utilisation",
        description=(
            "Endpoint pour afficher une condition d`utilisation par ID."
        ),
        responses={
            200: OpenApiResponse(
                description="Conditions récupérées avec succès",
                response=ConditionDutilisationAdminSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "message": "Liste des conditions récupérée avec succès",
                            "data": [
                                {
                                    "condition_id": "COND_1",
                                    "titre": {"fr": "Conditions FR", "en": "Terms EN", "ar": "الشروط AR"},
                                    "contenu": {"fr": "Contenu FR", "en": "Content EN", "ar": "المحتوى AR"},
                                    "version": 1,
                                    "active": True,
                                    "date_creation": "2025-12-20T16:30:00Z",
                                    "historique_modifications": ["Créé le 2025-12-20 16:30:00"]
                                }
                            ]
                        }
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
            )
        }
    )
    def get(self, request, condition_id):
        try:
            if request.user.is_authenticated:
                # Admins → toutes les conditions
                conditions = ConditionDutilisation.objects.get(condition_id=condition_id)
                serializer = ConditionDutilisationAdminSerializer(conditions)
            else:
                # Public → seulement les conditions actives
                conditions = ConditionDutilisation.objects.get(condition_id=condition_id)
                serializer = ConditionDutilisationPublicSerializer(conditions)

            return Response(
                {"status": True, "message": "récupérée avec succès", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Erreur dans AfficherConditionDutilisationDetailView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
