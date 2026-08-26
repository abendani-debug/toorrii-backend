from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVNombreAbsentSerializer


class RDVNombreAbsentView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre de clients absents",
        description="""
Retourne le nombre total de RDV avec statut 'Absent'.

Filtres disponibles :
- date
- mois
- année
- intervalle de dates
        """,
        parameters=[
            OpenApiParameter(name="date", type=str, required=False),
            OpenApiParameter(name="mois", type=int, required=False),
            OpenApiParameter(name="annee", type=int, required=False),
            OpenApiParameter(name="date_debut", type=str, required=False),
            OpenApiParameter(name="date_fin", type=str, required=False),
        ],
        responses=RDVNombreAbsentSerializer
    )
    def get(self, request):

        # ==========================
        # BASE QUERY
        # ==========================
        rdvs = RDV.objects.filter(statut_rdv="Absent")

        # ==========================
        # FILTER: DATE EXACTE
        # ==========================
        date_str = request.query_params.get("date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                rdvs = rdvs.filter(date_heure_rdv__date=date_obj)
            except ValueError:
                return Response(
                    {"detail": "Format date invalide (YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ==========================
        # FILTER: MOIS
        # ==========================
        mois = request.query_params.get("mois")
        if mois:
            try:
                rdvs = rdvs.filter(date_heure_rdv__month=int(mois))
            except ValueError:
                return Response(
                    {"detail": "Mois invalide (1-12)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ==========================
        # FILTER: ANNEE
        # ==========================
        annee = request.query_params.get("annee")
        if annee:
            try:
                rdvs = rdvs.filter(date_heure_rdv__year=int(annee))
            except ValueError:
                return Response(
                    {"detail": "Année invalide."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ==========================
        # FILTER: INTERVALLE
        # ==========================
        date_debut = request.query_params.get("date_debut")
        date_fin = request.query_params.get("date_fin")

        if date_debut and date_fin:
            try:
                debut = datetime.strptime(date_debut, "%Y-%m-%d").date()
                fin = datetime.strptime(date_fin, "%Y-%m-%d").date()

                rdvs = rdvs.filter(
                    date_heure_rdv__date__gte=debut,
                    date_heure_rdv__date__lte=fin
                )
            except ValueError:
                return Response(
                    {"detail": "Format intervalle invalide (YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ==========================
        # RESULT
        # ==========================
        return Response(
            {"nombre_clients_absents": rdvs.count()},
            status=status.HTTP_200_OK
        )