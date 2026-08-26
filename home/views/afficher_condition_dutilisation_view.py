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

class AfficherConditionDutilisationView(APIView):
    """
    Endpoint pour afficher les conditions d'utilisation.
    Les admins voient toutes les conditions.
    Le public ne voit que celles actives.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Afficher les conditions d'utilisation",
        description=(
            "Récupère toutes les conditions d'utilisation.\n"
            "- Pour les utilisateurs authentifiés (admins), toutes les conditions sont retournées.\n"
            "- Pour le public, seules les conditions actives sont retournées."
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
    def get(self, request):
        try:
            if request.user.is_authenticated:
                # Admins → toutes les conditions
                conditions = ConditionDutilisation.objects.all().order_by('-date_creation')
                serializer = ConditionDutilisationAdminSerializer(conditions, many=True)
            else:
                # Public → seulement les conditions actives
                conditions = ConditionDutilisation.objects.filter(active=True)
                serializer = ConditionDutilisationPublicSerializer(conditions, many=True)

            return Response(
                {"status": True, "message": "Liste des conditions récupérée avec succès", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Erreur dans AfficherConditionDutilisationView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
