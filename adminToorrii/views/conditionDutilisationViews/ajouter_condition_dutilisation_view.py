from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import ConditionDutilisation
from adminToorrii.serializers import ConditionDutilisationAdminSerializer as ConditionDutilisationSerializer
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class AjouterConditionDutilisationView(APIView):
    """
    POST /api/condition/ajouter/
    Endpoint pour ajouter une nouvelle condition d'utilisation.
    Accessible uniquement aux admins actifs.
     Une seule condition peut être active à la fois.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Condition D'utilisation"],
        summary="Ajouter une condition d'utilisation",
        description=(
            "Crée une nouvelle condition d'utilisation.\n\n"
            "Seuls les administrateurs actifs (`etat_compte='A'`) peuvent effectuer cette action.\n"
            "⚠ Si la condition est ajoutée avec `active=True`, toutes les autres conditions actives seront automatiquement désactivées."
        ),
        request=ConditionDutilisationSerializer,
        responses={
            201: OpenApiResponse(
                description="Condition créée avec succès",
                response=ConditionDutilisationSerializer,
                examples=[
                    OpenApiExample(
                        "Réponse 201",
                        value={
                            "status": True,
                            "message": "Condition d’utilisation ajoutée avec succès",
                            "data": {
                                "condition_id": "COND_1",
                                "titre": {"fr": "Titre FR", "en": "Title EN", "ar": "عنوان AR"},
                                "contenu": {"fr": "Contenu FR", "en": "Content EN", "ar": "محتوى AR"},
                                "version": 1,
                                "active": True,
                                "date_creation": "2025-12-20T17:00:00Z",
                                "historique_modifications": ["Créé le 2025-12-20 17:00:00"]
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Données invalides",
                examples=[
                    OpenApiExample(
                        "Réponse 400",
                        value={
                            "status": False,
                            "message": "Données invalides",
                            "details": {"titre": ["Clé manquante"]}
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Compte admin inactif ou accès refusé",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={"status": False, "message": "Admin non actif. Action non autorisée."}
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
    def post(self, request):
        try:

            # Validation des données
            serializer = ConditionDutilisationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"status": False, "message": "Données invalides", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Désactiver toutes les autres conditions si la nouvelle est active
            if serializer.validated_data.get('active', False):
                ConditionDutilisation.objects.filter(active=True).update(active=False)

            # Sauvegarde → génère condition_id automatiquement
            condition = serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Condition d’utilisation ajoutée avec succès",
                    "data": ConditionDutilisationSerializer(condition).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error("Erreur dans AjouterConditionDutilisationView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )