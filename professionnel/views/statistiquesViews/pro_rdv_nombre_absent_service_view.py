from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProAbsentParServiceSerializer


class ProRDVAbsentParServiceView(APIView):
    """
    Nombre d'absences par service pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Absences par service (Pro)",
        description="Retourne le nombre de clients absents par service du professionnel connecté.",
        responses=ProAbsentParServiceSerializer
    )
    def get(self, request):

        professionnel = request.user.professionnel

        rdvs = RDV.objects.filter(
            service__professionnel=professionnel,
            statut_rdv="Absent"
        )

        data_qs = rdvs.values(
            "service__service_id",
            "service__nom_service"
        ).annotate(
            nombre_clients_absents=Count("id")
        )

        data = {
            "services": [
                {
                    "service_id": item["service__service_id"],
                    "service_nom": item["service__nom_service"],
                    "nombre_clients_absents": item["nombre_clients_absents"]
                }
                for item in data_qs
            ]
        }

        serializer = ProAbsentParServiceSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)