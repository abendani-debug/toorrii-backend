from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Categorie


class SupprimerCategorieView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Catégories"],
        summary="Supprimer une catégorie",
        description=(
            "Cette opération supprime définitivement une catégorie de la base de données. "
            "**Attention : cette action est irréversible.**"
        ),
        responses={
            200: OpenApiResponse(
                description="Catégorie supprimée avec succès.",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "status": True,
                            "message": "Catégorie supprimée définitivement."
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Catégorie introuvable.",
                examples=[
                    OpenApiExample(
                        "Erreur 404",
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
    def delete(self, request, categorie_id):
        """Supprime une catégorie définitivement."""
        try:
            # Vérifier si la catégorie existe
            try:
                categorie = Categorie.objects.get(pk=categorie_id)
            except Categorie.DoesNotExist:
                return Response(
                    {"status": False, "error": "Catégorie introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Supprimer définitivement
            categorie.delete()

            return Response(
                {
                    "status": True,
                    "message": "Catégorie supprimée définitivement."
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "status": False,
                    "error": "Erreur interne du serveur.",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
