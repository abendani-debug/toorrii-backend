from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreTotalRDVSerializer


class NombreTotalRdvView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre total de RDV",
        description="Retourne le nombre total de rendez-vous enregistrés dans le système.",
        responses=NombreTotalRDVSerializer
    )
    def get(self, request):

        total = RDV.objects.count()

        return Response(
            {"total_rdvs": total},
            status=status.HTTP_200_OK
        )