from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import Categorie
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreTotalCategoriesSerializer


class NombreTotalCategoriesView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre total de catégories",
        description="Retourne le nombre total de catégories en base de données.",
        responses=NombreTotalCategoriesSerializer
    )
    def get(self, request):

        total = Categorie.objects.count()

        return Response(
            {"total_categories": total},
            status=status.HTTP_200_OK
        )