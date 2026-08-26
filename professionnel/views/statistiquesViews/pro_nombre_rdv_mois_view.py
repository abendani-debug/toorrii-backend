from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from datetime import datetime

from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVParMoisSerializer
from adminToorrii.models import RDV


class ProRDVParMoisView(APIView):
    """
    Statistiques des RDV par mois pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Statistiques RDV par mois (Pro)",
        description="Retourne les statistiques des RDV du professionnel pour un mois précis.",
        parameters=[
            OpenApiParameter(
                name="mois",
                type=int,
                required=True,
                description="Mois (1-12)"
            ),
            OpenApiParameter(
                name="annee",
                type=int,
                required=True,
                description="Année (ex: 2026)"
            )
        ],
        responses=ProRDVParMoisSerializer
    )
    def get(self, request):

        mois = request.query_params.get("mois")
        annee = request.query_params.get("annee")

        if not mois or not annee:
            return Response(
                {"detail": "Les paramètres mois et année sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mois = int(mois)
            annee = int(annee)

            if not (1 <= mois <= 12):
                raise ValueError

        except ValueError:
            return Response(
                {"detail": "Mois doit être entre 1-12 et année valide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        professionnel = request.user.professionnel

        rdvs = RDV.objects.filter(
            service__professionnel=professionnel,
            date_heure_rdv__month=mois,
            date_heure_rdv__year=annee
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

        serializer = ProRDVParMoisSerializer({
            "mois": mois,
            "annee": annee,
            "total_rdv": total_rdv,
            "rdv_par_statut": rdv_par_statut
        })

        return Response(serializer.data, status=status.HTTP_200_OK)