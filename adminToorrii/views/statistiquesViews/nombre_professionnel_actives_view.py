from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import Professionnel
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreProfessionnelsActifsSerializer


class NombreTotalProfessionnelsActivesView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre de professionnels actifs",
        description="Retourne le nombre total de professionnels ayant un compte actif.",
        responses=NombreProfessionnelsActifsSerializer
    )
    def get(self, request):

        total_actifs = Professionnel.objects.filter(
            etat_compte='A'
        ).count()

        return Response(
            {"total_professionnels_actifs": total_actifs},
            status=status.HTTP_200_OK
        )