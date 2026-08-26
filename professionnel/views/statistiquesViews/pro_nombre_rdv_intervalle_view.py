from django.db.models import Count
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVParIntervalleSerializer


class ProRDVParIntervalleView(APIView):
    """
    Statistiques des RDV par intervalle pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Statistiques RDV par intervalle (Pro)",
        description="Retourne les statistiques des RDV du professionnel pour une période donnée.",
        parameters=[
            OpenApiParameter(
                name="date_debut",
                type=str,
                required=True,
                description="Format YYYY-MM-DD"
            ),
            OpenApiParameter(
                name="date_fin",
                type=str,
                required=True,
                description="Format YYYY-MM-DD"
            )
        ],
        responses=ProRDVParIntervalleSerializer
    )
    def get(self, request):

        date_debut_str = request.query_params.get("date_debut")
        date_fin_str = request.query_params.get("date_fin")

        if not date_debut_str or not date_fin_str:
            return Response(
                {"detail": "Les paramètres date_debut et date_fin sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Format de date invalide (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if date_debut > date_fin:
            return Response(
                {"detail": "date_debut doit être <= date_fin."},
                status=status.HTTP_400_BAD_REQUEST
            )

        professionnel = request.user.professionnel

        rdvs = RDV.objects.filter(
            service__professionnel=professionnel,
            date_heure_rdv__date__gte=date_debut,
            date_heure_rdv__date__lte=date_fin
        )

        total_rdv = rdvs.count()

        stats_qs = rdvs.values("statut_rdv").annotate(total=Count("id"))

        rdv_par_statut = {
            "En_attente": 0,
            "Confirmer": 0,
            "Annuler": 0,
            "Absent": 0,
            "Terminer": 0,
        }

        for item in stats_qs:
            rdv_par_statut[item["statut_rdv"]] = item["total"]

        serializer = ProRDVParIntervalleSerializer({
            "date_debut": date_debut,
            "date_fin": date_fin,
            "total_rdv": total_rdv,
            "rdv_par_statut": rdv_par_statut
        })

        return Response(serializer.data, status=status.HTTP_200_OK)