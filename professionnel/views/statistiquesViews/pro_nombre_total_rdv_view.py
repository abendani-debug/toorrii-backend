from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVTotalSerializer


class ProNombreTotalRDVView(APIView):
    """
    Endpoint : Nombre total de RDV du professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Nombre total de RDV (professionnel connecté)",
        description="""
Retourne le nombre total de rendez-vous liés aux services
du professionnel connecté.
        """,
        responses={200: ProRDVTotalSerializer},
        examples=[
            OpenApiExample(
                "Exemple",
                value={"total_rdv": 128}
            )
        ]
    )
    def get(self, request):

        professionnel = request.user.professionnel

        total = RDV.objects.filter(
            service__professionnel=professionnel
        ).count()

        data = {
            "total_rdv": total
        }

        serializer = ProRDVTotalSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)