from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVPresentSerializer


class ProRDVNombrePresentView(APIView):
    """
    Nombre total des clients présents (Terminer)
    pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Nombre de clients présents (Pro)",
        description="Retourne le nombre total de rendez-vous terminés (clients présents).",
        responses=ProRDVPresentSerializer
    )
    def get(self, request):

        professionnel = request.user.professionnel

        nombre_presents = RDV.objects.filter(
            service__professionnel=professionnel,
            statut_rdv="Terminer"
        ).count()

        serializer = ProRDVPresentSerializer({
            "nombre_clients_presents": nombre_presents
        })

        return Response(serializer.data, status=status.HTTP_200_OK)