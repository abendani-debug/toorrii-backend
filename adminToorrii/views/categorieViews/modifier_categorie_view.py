from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Categorie
from adminToorrii.serializers import CategorieSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)


class ModifierCategorieView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Catégories"],
        summary="Modifier une catégorie",
        description="Met à jour une catégorie existante identifiée par son `categorie_id`.",
        request=CategorieSerializer,
        responses={
            200: OpenApiResponse(
                description="Catégorie mise à jour avec succès",
                response=CategorieSerializer,
                examples=[
                    OpenApiExample(
                        "Exemple 200",
                        value={
                            "status": True,
                            "message": "Catégorie mise à jour avec succès",
                            "data": {
                                "categorie_id": "CAT5",
                                "nom_categorie": "Mode & Style",
                                "description_categorie": "Toutes les nouveautés mode",
                                "couleur_theme": "#AA44FF",
                                "ordre_affichage": 2,
                                "photo_principale_cat": "/media/categories/cat5.jpg",
                                "active": True,
                                "date_creation": "2025-11-20T13:40:00Z"
                            }
                        }
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Données invalides",
                examples=[
                    OpenApiExample(
                        "Exemple 400",
                        value={
                            "status": False,
                            "errors": {
                                "nom_categorie": ["Ce champ doit être unique."]
                            }
                        }
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Catégorie introuvable",
                examples=[
                    OpenApiExample(
                        "Exemple 404",
                        value={
                            "status": False,
                            "message": "Catégorie non trouvée"
                        }
                    )
                ],
            ),
            500: OpenApiResponse(
                description="Erreur interne",
                examples=[
                    OpenApiExample(
                        "Exemple 500",
                        value={"status": False, "error": "Une erreur interne est survenue"}
                    )
                ],
            ),
        }
    )
    def put(self, request, categorie_id):
        try:
            # Vérifier si la catégorie existe
            try:
                categorie = Categorie.objects.get(categorie_id=categorie_id)
            except Categorie.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Catégorie non trouvée"
                }, status=status.HTTP_404_NOT_FOUND)

            # Mise à jour partielle (partial=True → champs non obligatoires)
            serializer = CategorieSerializer(
                categorie, 
                data=request.data, 
                partial=True
            )

            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            categorie = serializer.save()

            return Response({
                "status": True,
                "message": "Catégorie mise à jour avec succès",
                "data": CategorieSerializer(categorie).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Erreur dans ModifierCategorieView : %s", str(e))
            return Response({
                "status": False,
                "error": "Une erreur interne est survenue"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
