from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import Service
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreTotalServicesSerializer


class NombreTotalServicesView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre total de services",
        description="Retourne le nombre total de services dans la base de données.",
        responses=NombreTotalServicesSerializer
    )
    def get(self, request):

        total = Service.objects.count()

        data = {
            "total_services": total
        }

        return Response(data, status=status.HTTP_200_OK)