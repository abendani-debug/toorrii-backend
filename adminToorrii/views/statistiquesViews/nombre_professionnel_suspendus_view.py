from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import Professionnel
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreProfessionnelsSuspendusSerializer


class NombreTotalProfessionnelsSuspendusView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre de professionnels suspendus",
        description="Retourne le nombre total de professionnels dont le compte est suspendu.",
        responses=NombreProfessionnelsSuspendusSerializer
    )
    def get(self, request):

        total_suspendus = Professionnel.objects.filter(
            etat_compte='SUSP'
        ).count()

        return Response(
            {"total_professionnels_suspendus": total_suspendus},
            status=status.HTTP_200_OK
        )