from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Categorie
from adminToorrii.serializers import CategorieSerializer


class SuspendreCategorieView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        request=None,
        tags=["Catégories"],
        summary="Suspendre une catégorie",
        description=(
            "Cette opération met le champ `active = false` pour la catégorie spécifiée. "
            "Elle permet de désactiver une catégorie sans la supprimer."
        ),
        responses={
            200: OpenApiResponse(
                response=CategorieSerializer,
                description="Catégorie suspendue avec succès.",
                examples=[
                    OpenApiExample(
                        "Catégorie désactivée",
                        value={
                            "status": True,
                            "message": "Catégorie suspendue avec succès.",
                            "data": {
                                "nom_categorie": "Technologie",
                                "description_categorie": "Catégorie des produits tech",
                                "couleur_theme": "#FF0000",
                                "ordre_affichage": 1,
                                "photo_principale_cat": "/media/cat/tech.png",
                                "active": False,
                            },
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Catégorie non trouvée.",
                examples=[
                    OpenApiExample(
                        "Catégorie introuvable",
                        value={"status": False, "error": "Catégorie introuvable."},
                    )
                ],
            ),
            500: OpenApiResponse(
                description="Erreur serveur.",
                examples=[
                    OpenApiExample(
                        "Erreur interne",
                        value={"status": False, "error": "Erreur interne du serveur."},
                    )
                ],
            ),
        },
    )
    def put(self, request, categorie_id):
        """Suspendre une catégorie en mettant active = False"""

        try:
            # 1) Vérifier si la catégorie existe
            try:
                categorie = Categorie.objects.get(pk=categorie_id)
            except Categorie.DoesNotExist:
                return Response(
                    {"status": False, "error": "Catégorie introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 2) Mettre active = False
            categorie.active = False
            categorie.save()

            serializer = CategorieSerializer(categorie)

            return Response(
                {
                    "status": True,
                    "message": "Catégorie suspendue avec succès.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            # Loggable error
            return Response(
                {
                    "status": False,
                    "error": "Erreur interne du serveur.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
