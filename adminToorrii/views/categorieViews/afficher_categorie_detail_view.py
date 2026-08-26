from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter
import logging

from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Categorie
from adminToorrii.serializers import CategorieAfficherSerializer

logger = logging.getLogger(__name__)


class AfficherCategoriesDetailView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Catégories"],
        summary="Récupérer le détail d'une catégorie",
        description=(
            "Retourne les informations détaillées d'une catégorie spécifique à partir de son `categorie_id`.\n\n"
            "**Notes :**\n"
            "- Accessible uniquement aux administrateurs (`IsAdminUserCustom`).\n"
            "- Retourne une erreur 404 si la catégorie n'existe pas.\n"
        ),
        parameters=[
            OpenApiParameter(
                name="categorie_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID unique de la catégorie"
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Détail de la catégorie récupéré avec succès",
                response=CategorieAfficherSerializer,
                examples=[
                    OpenApiExample(
                        name="Succès",
                        summary="Réponse 200",
                        value={
                            "status": True,
                            "data": {
                                "id": 1,
                                "titre": "Mode",
                                "ordre_affichage": 1,
                                "description": "Catégorie vêtements",
                                "date_creation": "2025-12-01T10:45:00Z",
                                "date_modification": "2025-12-01T10:45:00Z"
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Catégorie non trouvée",
                examples=[
                    OpenApiExample(
                        name="Non trouvée",
                        summary="Réponse 404",
                        value={
                            "status": False,
                            "message": "Categorie non trouvé."
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne du serveur",
                examples=[
                    OpenApiExample(
                        name="Erreur interne",
                        summary="Réponse 500",
                        value={
                            "status": False,
                            "error": "Une erreur interne est survenue."
                        }
                    )
                ]
            ),
        }
    )
    def get(self, request, categorie_id):
        try:
            try:
                categorie = Categorie.objects.get(categorie_id=categorie_id)
            except Categorie.DoesNotExist:
                return Response(
                    {"status": False, "message": "Categorie non trouvé."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CategorieAfficherSerializer(categorie)
            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Erreur dans AfficherCategoriesDetailView: %s", str(e))
            return Response(
                {"status": False, "error": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )