from datetime import datetime
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVParJourSerializer


class ProRDVParJourView(APIView):
    """
    Statistiques des RDV par jour pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Statistiques RDV par jour (Pro)",
        description="Retourne les statistiques des RDV du professionnel pour une date précise.",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                required=True,
                description="Format YYYY-MM-DD"
            )
        ],
        responses=ProRDVParJourSerializer
    )
    def get(self, request):

        date_str = request.query_params.get("date")

        if not date_str:
            return Response(
                {"detail": "Le paramètre date est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Format de date invalide (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        professionnel = request.user.professionnel

        rdvs = RDV.objects.filter(
            service__professionnel=professionnel,
            date_heure_rdv__date=date_obj
        )

        total_rdv = rdvs.count()

        # stats par statut
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

        serializer = ProRDVParJourSerializer({
            "date": date_obj,
            "total_rdv": total_rdv,
            "rdv_par_statut": rdv_par_statut
        })

        return Response(serializer.data, status=status.HTTP_200_OK)