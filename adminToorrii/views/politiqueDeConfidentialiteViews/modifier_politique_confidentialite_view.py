from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import PolitiqueConfidentialite
from adminToorrii.serializers import PolitiqueConfidentialiteAdminSerializer as PolitiqueConfidentialiteSerializer
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class ModifierPolitiqueView(APIView):
    """
    PUT /api/politique/modifier/<politique_id>/
    Endpoint pour modifier une politique de confidentialité existante.
    Seuls les admins actifs peuvent modifier.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Politique de confidentialité"],
        summary="Modifier une politique de confidentialité existante",
        description=(
            "Modifie une politique de confidentialité identifiée par `politique_id`.\n\n"
            "⚠ Une seule politique peut être active à la fois. "
            "Si la modification active cette politique, toutes les autres seront désactivées automatiquement.\n\n"
            "Seuls les administrateurs actifs (`etat_compte='A'`) peuvent effectuer cette action."
        ),
        request=PolitiqueConfidentialiteSerializer,
        responses={
            200: OpenApiResponse(
                description="Politique modifiée avec succès",
                response=PolitiqueConfidentialiteSerializer(many=False),
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "message": "Politique modifiée avec succès",
                            "data": {
                                "politique_id": "POL_2",
                                "titre": {"fr": "Politique modifiée", "en": "Modified Policy", "ar": "سياسة معدلة"},
                                "contenu": {"fr": "Contenu FR modifié", "en": "Content EN modified", "ar": "المحتوى AR المعدل"},
                                "version": 2,
                                "active": True,
                                "date_creation": "2025-12-20T15:00:00Z",
                                "historique_modifications": [
                                    "Créé le 2025-12-20 15:00:00",
                                    "Modifié le 2025-12-20 16:00:00"
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
                        value={
                            "status": False,
                            "message": "Données invalides",
                            "details": {
                                "titre": ["Clé 'en' manquante."],
                                "version": ["Cette version existe déjà."]
                            }
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Compte admin inactif ou accès refusé",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={"status": False, "message": "Compte admin inactif. Action non autorisée."}
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Politique non trouvée",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Politique avec ID POL_99 non trouvée."}
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
    def put(self, request, politique_id):
        try:
            # Vérifier si l'admin est actif
            if request.user.etat_compte != "A":
                return Response(
                    {"status": False, "message": "Compte admin inactif. Action non autorisée."},
                    status=status.HTTP_403_FORBIDDEN
                )

            try:
                politique = PolitiqueConfidentialite.objects.get(politique_id=politique_id)
            except PolitiqueConfidentialite.DoesNotExist:
                return Response(
                    {"status": False, "message": f"Politique avec ID {politique_id} non trouvée."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = PolitiqueConfidentialiteSerializer(politique, data=request.data, partial=False)
            if serializer.is_valid():
                #  Si la politique est active, désactiver toutes les autres
                if serializer.validated_data.get('active', False):
                    PolitiqueConfidentialite.objects.exclude(politique_id=politique_id).filter(active=True).update(active=False)

                serializer.save()
                return Response(
                    {"status": True, "message": "Politique modifiée avec succès", "data": serializer.data},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"status": False, "message": "Données invalides", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error("Erreur dans ModifierPolitiqueView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )