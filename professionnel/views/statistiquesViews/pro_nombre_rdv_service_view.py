from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVParServiceSerializer


class ProNombreRDVParServiceView(APIView):
    """
    Endpoint : Nombre de rendez-vous par service (professionnel connecté)
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Nombre de RDV par service",
        description="""
Retourne le nombre de rendez-vous regroupés par service
du professionnel connecté.
        """,
        responses={200: ProRDVParServiceSerializer},
        examples=[
            OpenApiExample(
                "Exemple",
                value={
                    "services": [
                        {
                            "service_id": "SER_1",
                            "service_nom": "Consultation",
                            "total_rdv": 25
                        },
                        {
                            "service_id": "SER_2",
                            "service_nom": "Vaccination",
                            "total_rdv": 10
                        }
                    ]
                }
            )
        ]
    )
    def get(self, request):

        professionnel = request.user.professionnel

        rdvs = (
            RDV.objects
            .filter(service__professionnel=professionnel)
            .values(
                "service__service_id",
                "service__nom_service"
            )
            .annotate(total_rdv=Count("id"))
        )

        services_data = [
            {
                "service_id": item["service__service_id"],
                "service_nom": item["service__nom_service"],
                "total_rdv": item["total_rdv"]
            }
            for item in rdvs
        ]

        data = {
            "services": services_data
        }

        serializer = ProRDVParServiceSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)