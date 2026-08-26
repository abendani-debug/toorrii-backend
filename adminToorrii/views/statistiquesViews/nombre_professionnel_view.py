from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import Professionnel
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreTotalProfessionnelsSerializer


class NombreTotalProfessionnelsView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre total de professionnels",
        description="Retourne le nombre total de professionnels enregistrés dans le système.",
        responses=NombreTotalProfessionnelsSerializer
    )
    def get(self, request):

        total = Professionnel.objects.count()

        return Response(
            {"total_professionnels": total},
            status=status.HTTP_200_OK
        )