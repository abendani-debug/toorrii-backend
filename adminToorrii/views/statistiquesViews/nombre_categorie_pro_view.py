from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import Categorie, Professionnel
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreProfessionnelsParCategorieSerializer


class NombreTotalCategoriesProView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre de professionnels par catégorie",
        description="""
Retourne le nombre de professionnels associés à une catégorie.

 Calcul basé sur les services liés à la catégorie.
        """,
        parameters=[
            OpenApiParameter(
                name="categorie_id",
                type=str,
                required=True,
                description="ID de la catégorie (ex: Cat_1)"
            )
        ],
        responses=NombreProfessionnelsParCategorieSerializer
    )
    def get(self, request):

        # ==========================
        # PARAM
        # ==========================
        categorie_id = request.query_params.get("categorie_id")

        if not categorie_id:
            return Response(
                {"error": "categorie_id est obligatoire"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================
        # GET CATEGORY
        # ==========================
        try:
            categorie = Categorie.objects.get(categorie_id=categorie_id)
        except Categorie.DoesNotExist:
            return Response(
                {"error": "Catégorie non trouvée"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================
        # COUNT PROFESSIONNELS
        # ==========================
        total_professionnels = Professionnel.objects.filter(
            services__categorie=categorie
        ).distinct().count()

        # ==========================
        # RESPONSE
        # ==========================
        data = {
            "categorie_id": categorie.categorie_id,
            "categorie_nom": categorie.nom_categorie,
            "total_professionnels": total_professionnels
        }

        return Response(data, status=status.HTTP_200_OK)