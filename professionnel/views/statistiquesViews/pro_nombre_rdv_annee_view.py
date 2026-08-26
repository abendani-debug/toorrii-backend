from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ProRDVParAnneeSerializer


class ProRDVParAnneeView(APIView):
    """
    Statistiques des RDV par année pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Statistiques RDV par année (Pro)",
        description="Retourne les statistiques des RDV du professionnel pour une année précise.",
        parameters=[
            OpenApiParameter(
                name="annee",
                type=int,
                required=True,
                description="Année (ex: 2026)"
            )
        ],
        responses=ProRDVParAnneeSerializer
    )
    def get(self, request):

        annee = request.query_params.get("annee")

        if not annee:
            return Response(
                {"detail": "Le paramètre année est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            annee = int(annee)
        except ValueError:
            return Response(
                {"detail": "Année invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        professionnel = request.user.professionnel

        rdvs = RDV.objects.filter(
            service__professionnel=professionnel,
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

        serializer = ProRDVParAnneeSerializer({
            "annee": annee,
            "total_rdv": total_rdv,
            "rdv_par_statut": rdv_par_statut
        })

        return Response(serializer.data, status=status.HTTP_200_OK)