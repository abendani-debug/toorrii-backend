from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import Professionnel
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreProfessionnelsSupprimesSerializer


class NombreTotalProfessionnelsSupprimesView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre de professionnels supprimés",
        description="Retourne le nombre total de professionnels dont le compte est supprimé.",
        responses=NombreProfessionnelsSupprimesSerializer
    )
    def get(self, request):

        total_supprimes = Professionnel.objects.filter(
            etat_compte='SUP'
        ).count()

        return Response(
            {"total_professionnels_supprimes": total_supprimes},
            status=status.HTTP_200_OK
        )