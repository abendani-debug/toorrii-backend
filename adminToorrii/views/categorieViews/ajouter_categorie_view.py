from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Categorie
from adminToorrii.serializers import CategorieSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)


class AjouterCategorieView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Catégories"],
        summary="Ajouter une nouvelle catégorie",
        description=(
            "Crée une nouvelle catégorie dans le système. "
            "Si ordre_affichage n`est pas fourni, il prendra automatiquement la dernière position."
        ),
        request=CategorieSerializer,
        responses={
            201: OpenApiResponse(
                description="Catégorie créée avec succès",
                response=CategorieSerializer,
                examples=[
                    OpenApiExample(
                        "Exemple 201",
                        value={
                            "status": True,
                            "message": "Catégorie créée avec succès",
                            "data": {
                                "categorie_id": "CAT12",
                                "nom_categorie": "Mode",
                                "description_categorie": "Vêtements",
                                "couleur_theme": "#FF3355",
                                "ordre_affichage": 3,
                                "photo_principale_cat": "/media/categories/cat.jpg",
                                "active": True,
                                "date_creation": "2025-12-02T10:00:00Z",
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Données invalides",
                examples=[
                    OpenApiExample(
                        "Exemple 400",
                        value={
                            "status": False,
                            "errors": {
                                "nom_categorie": ["Ce champ est requis."]
                            }
                        }
                    )
                ],
            ),
            500: OpenApiResponse(
                description="Erreur interne du serveur",
                examples=[
                    OpenApiExample(
                        "Exemple 500",
                        value={
                            "status": False,
                            "error": "Une erreur interne est survenue"
                        }
                    )
                ]
            ),
        }
    )
    def post(self, request):
        try:
            data = request.data.copy()

            serializer = CategorieSerializer(data=data)

            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            categorie = Categorie.objects.create(
                nom_categorie=serializer.validated_data['nom_categorie'],
                description_categorie=serializer.validated_data['description_categorie'],
                couleur_theme=serializer.validated_data.get('couleur_theme', ''),
                ordre_affichage=serializer.validated_data.get('ordre_affichage') or 0,
                photo_principale_cat=serializer.validated_data.get('photo_principale_cat'),
                active=serializer.validated_data.get('active', True),
                parent=serializer.validated_data.get('parent'),
            )


            return Response({
                "status": True,
                "message": "Catégorie créée avec succès",
                "data": CategorieSerializer(categorie).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error("Erreur dans AjouterCategorieView : %s", str(e))
            return Response({
                "status": False,
                "error": "Une erreur interne est survenue"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
