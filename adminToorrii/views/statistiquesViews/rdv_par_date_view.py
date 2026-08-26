from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.db.models import Count

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVStatsParDateGlobalSerializer


class RDVStatsParDateGlobalView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques complètes des RDV par date",
        description="""
Retourne les statistiques globales des RDV pour une date donnée :

- total RDV
- par statut
- par mode de réservation
- par source de création
        """,
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                required=False,
                description="Format YYYY-MM-DD (default = today)"
            )
        ],
        responses=RDVStatsParDateGlobalSerializer
    )
    def get(self, request):

        # ==========================
        # DATE HANDLING
        # ==========================
        date_str = request.query_params.get("date")

        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Format de date invalide (YYYY-MM-DD)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            date_obj = datetime.today().date()

        # ==========================
        # QUERYSET
        # ==========================
        rdvs_qs = RDV.objects.filter(date_heure_rdv__date=date_obj)

        total_rdv = rdvs_qs.count()

        # ==========================
        # STATUTS
        # ==========================
        rdv_par_statut = {
            "En_attente": 0,
            "Confirmer": 0,
            "Annuler": 0,
            "Terminer": 0,
            "Absent": 0,
        }

        for item in rdvs_qs.values("statut_rdv").annotate(count=Count("rdv_id")):
            rdv_par_statut[item["statut_rdv"]] = item["count"]

        # ==========================
        # MODE RESERVATION
        # ==========================
        rdv_par_mode_reservation = {
            "En_ligne": 0,
            "Sur_place": 0,
        }

        for item in rdvs_qs.values("mode_reservation").annotate(count=Count("rdv_id")):
            rdv_par_mode_reservation[item["mode_reservation"]] = item["count"]

        # ==========================
        # SOURCE CREATION
        # ==========================
        rdv_par_source_creation = {
            "Client": 0,
            "Pro": 0,
            "Admin": 0,
        }

        for item in rdvs_qs.values("source_creation").annotate(count=Count("rdv_id")):
            rdv_par_source_creation[item["source_creation"]] = item["count"]

        # ==========================
        # RESPONSE STRUCTURE
        # ==========================
        response_data = {
            "date": date_obj,
            "total_rdv": total_rdv,
            "rdv_par_statut": rdv_par_statut,
            "rdv_par_mode_reservation": rdv_par_mode_reservation,
            "rdv_par_source_creation": rdv_par_source_creation,
        }

        serializer = RDVStatsParDateGlobalSerializer(response_data)

        return Response(serializer.data, status=status.HTTP_200_OK)