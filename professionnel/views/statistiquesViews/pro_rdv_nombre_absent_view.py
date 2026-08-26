from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVAbsentSerializer


class ProRDVNombreAbsentView(APIView):
    """
    Nombre de clients absents pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Nombre de clients absents (Pro)",
        description="Retourne le nombre de rendez-vous avec statut 'Absent' pour le professionnel connecté.",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                required=False,
                description="Filtre optionnel YYYY-MM-DD"
            ),
            OpenApiParameter(
                name="mois",
                type=int,
                required=False
            ),
            OpenApiParameter(
                name="annee",
                type=int,
                required=False
            )
        ],
        responses=ProRDVAbsentSerializer
    )
    def get(self, request):

        professionnel = request.user.professionnel

        rdvs = RDV.objects.filter(
            service__professionnel=professionnel,
            statut_rdv="Absent"
        )

        # filtre date optionnel
        date_str = request.query_params.get("date")
        if date_str:
            from datetime import datetime
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                rdvs = rdvs.filter(date_heure_rdv__date=date_obj)
            except ValueError:
                return Response(
                    {"detail": "Format date invalide (YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        mois = request.query_params.get("mois")
        if mois:
            rdvs = rdvs.filter(date_heure_rdv__month=int(mois))

        annee = request.query_params.get("annee")
        if annee:
            rdvs = rdvs.filter(date_heure_rdv__year=int(annee))

        serializer = ProRDVAbsentSerializer({
            "nombre_clients_absents": rdvs.count()
        })

        return Response(serializer.data, status=status.HTTP_200_OK)