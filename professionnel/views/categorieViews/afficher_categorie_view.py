from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import Categorie
from professionnel.serializers import CategorieAfficherSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
import logging

logger = logging.getLogger(__name__)


class AfficherCategoriesView(APIView):
    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Catégories"],
        summary="Récupérer la liste des catégories",
        description=(
            "Retourne toutes les catégories enregistrées dans le système, triées par `ordre_affichage`.\n\n"
            "**Notes :**\n"
            "- Accessible uniquement aux pros (`IsProfessionnelUserCustom`).\n"
            "- Retourne une erreur 404 si aucune catégorie n'est trouvée.\n"
            "- Tous les champs du modèle sont renvoyés (serializer en read-only)."
        ),
        responses={
            200: OpenApiResponse(
                description="Liste des catégories récupérée avec succès",
                response=CategorieAfficherSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        summary="Succès",
                        value={
                            "status": True,
                            "count": 2,
                            "data": [
                                {
                                    "id": 1,
                                    "titre": "Mode",
                                    "ordre_affichage": 1,
                                    "description": "Catégorie vêtements",
                                    "date_creation": "2025-12-01T10:45:00Z",
                                    "date_modification": "2025-12-01T10:45:00Z"
                                },
                                {
                                    "id": 2,
                                    "titre": "Électronique",
                                    "ordre_affichage": 2,
                                    "description": "Appareils et gadgets",
                                    "date_creation": "2025-12-01T11:00:00Z",
                                    "date_modification": "2025-12-01T11:00:00Z"
                                }
                            ]
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Aucune catégorie trouvée",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        summary="Aucune catégorie",
                        value={
                            "status": False,
                            "message": "Aucune catégorie trouvée."
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne du serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        summary="Erreur interne",
                        value={
                            "status": False,
                            "error": "Une erreur interne est survenue. Veuillez réessayer plus tard."
                        }
                    )
                ]
            ),
        }
    )
    def get(self, request):
        try:
            categories = Categorie.objects.filter(parent__isnull=True).order_by('ordre_affichage')

            if not categories.exists():
                return Response({
                    "status": False,
                    "message": "Aucune catégorie trouvée."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = CategorieAfficherSerializer(categories, many=True)

            return Response({
                "status": True,
                "count": categories.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Erreur interne dans AfficherCategoriesView : %s", str(e))
            return Response({
                "status": False,
                "error": "Une erreur interne est survenue. Veuillez réessayer plus tard."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
