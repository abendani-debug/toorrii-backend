from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from datetime import datetime

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVStatsParIntervalleSerializer


class RDVStatsParIntervalleView(APIView):
    """
    Endpoint : Statistiques des rendez-vous pour un intervalle de dates
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques RDV par intervalle de dates",
        description="""
Retourne les statistiques globales des RDV sur une période.
Inclut statut, mode de réservation et source de création.
        """,
        parameters=[
            OpenApiParameter(
                name="date_debut",
                type=str,
                required=True,
                description="YYYY-MM-DD"
            ),
            OpenApiParameter(
                name="date_fin",
                type=str,
                required=True,
                description="YYYY-MM-DD"
            ),
        ],
        responses={200: RDVStatsParIntervalleSerializer},
        examples=[
            OpenApiExample(
                "Exemple",
                value={
                    "date_debut": "2026-01-01",
                    "date_fin": "2026-01-31",
                    "total_rdv": 150,
                    "rdv_par_statut": {
                        "En_attente": 20,
                        "Confirmer": 110,
                        "Annuler": 10,
                        "Absent": 5,
                        "Terminer": 5
                    },
                    "rdv_par_mode_reservation": {
                        "En_ligne": 90,
                        "Sur_place": 60
                    },
                    "rdv_par_source_creation": {
                        "Client": 100,
                        "Pro": 40,
                        "Admin": 10
                    }
                }
            )
        ]
    )
    def get(self, request):

        date_debut_str = request.query_params.get("date_debut")
        date_fin_str = request.query_params.get("date_fin")

        if not date_debut_str or not date_fin_str:
            return Response(
                {"detail": "date_debut et date_fin sont obligatoires"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Format invalide YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if date_debut > date_fin:
            return Response(
                {"detail": "date_debut doit être <= date_fin"},
                status=status.HTTP_400_BAD_REQUEST
            )

        rdvs = RDV.objects.filter(
            date_heure_rdv__date__gte=date_debut,
            date_heure_rdv__date__lte=date_fin
        )

        total_rdv = rdvs.count()

        rdv_par_statut = {
            "En_attente": 0,
            "Confirmer": 0,
            "Annuler": 0,
            "Absent": 0,
            "Terminer": 0,
        }

        for item in rdvs.values("statut_rdv").annotate(count=Count("rdv_id")):
            rdv_par_statut[item["statut_rdv"]] = item["count"]

        rdv_par_mode = {
            "En_ligne": 0,
            "Sur_place": 0,
        }

        for item in rdvs.values("mode_reservation").annotate(count=Count("rdv_id")):
            rdv_par_mode[item["mode_reservation"]] = item["count"]

        rdv_par_source = {
            "Client": 0,
            "Pro": 0,
            "Admin": 0,
        }

        for item in rdvs.values("source_creation").annotate(count=Count("rdv_id")):
            rdv_par_source[item["source_creation"]] = item["count"]

        data = {
            "date_debut": date_debut,
            "date_fin": date_fin,
            "total_rdv": total_rdv,
            "rdv_par_statut": rdv_par_statut,
            "rdv_par_mode_reservation": rdv_par_mode,
            "rdv_par_source_creation": rdv_par_source,
        }

        return Response(data, status=status.HTTP_200_OK)