from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import ConditionDutilisation
from adminToorrii.serializers import ConditionDutilisationAdminSerializer as ConditionDutilisationSerializer
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
import logging

logger = logging.getLogger(__name__)

class ModifierConditionDutilisationView(APIView):
    """
    PUT /api/condition/modifier/<condition_id>/
    Endpoint pour modifier une condition d'utilisation existante.
    Accessible uniquement aux admins actifs.
     Si `active=True`, toutes les autres conditions sont désactivées automatiquement.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Condition D'utilisation"],
        summary="Modifier une condition d'utilisation existante",
        description=(
            "Met à jour une condition d'utilisation identifiée par `condition_id`.\n\n"
            "Seuls les administrateurs actifs (`etat_compte='A'`) peuvent effectuer cette action.\n"
            " Si la condition est mise à `active=True`, toutes les autres conditions actives seront désactivées."
        ),
        parameters=[
            OpenApiParameter(
                name="condition_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID de la condition d'utilisation à modifier",
                required=True
            )
        ],
        request=ConditionDutilisationSerializer,
        responses={
            200: OpenApiResponse(
                description="Condition modifiée avec succès",
                response=ConditionDutilisationSerializer,
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "message": "Condition d’utilisation modifiée avec succès",
                            "data": {
                                "condition_id": "COND_1",
                                "titre": {"fr": "Titre FR modifié", "en": "Title EN modifié", "ar": "عنوان AR modifié"},
                                "contenu": {"fr": "Contenu FR modifié", "en": "Content EN modifié", "ar": "محتوى AR modifié"},
                                "version": 2,
                                "active": True,
                                "date_creation": "2025-12-20T17:00:00Z",
                                "historique_modifications": [
                                    "Créé le 2025-12-19 12:00:00",
                                    "Modifié le 2025-12-20 17:00:00"
                                ]
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
                        value={"status": False, "message": "Données invalides", "details": {"titre": ["Clé manquante"]}}
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Compte admin inactif ou non autorisé",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={"status": False, "message": "Admin non actif. Action non autorisée."}
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Condition introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Condition d’utilisation introuvable."}
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
    def put(self, request, condition_id):
        try:
            # Récupérer la condition
            try:
                condition = ConditionDutilisation.objects.get(condition_id=condition_id)
            except ConditionDutilisation.DoesNotExist:
                return Response(
                    {"status": False, "message": "Condition d’utilisation introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Mise à jour via serializer
            serializer = ConditionDutilisationSerializer(condition, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    {"status": False, "message": "Données invalides", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Si active=True, désactive toutes les autres
            if serializer.validated_data.get("active", False):
                ConditionDutilisation.objects.exclude(pk=condition.pk).update(active=False)

            # Sauvegarde de la condition mise à jour
            condition_updated = serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Condition d’utilisation modifiée avec succès",
                    "data": ConditionDutilisationSerializer(condition_updated).data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Erreur dans ModifierConditionDutilisationView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )