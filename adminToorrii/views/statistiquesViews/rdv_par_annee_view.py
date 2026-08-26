from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from django.db.models import Count

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVStatsParAnneeSerializer


class RDVStatsParAnneeView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques des RDV par année",
        description="""
Retourne les statistiques globales des RDV pour une année donnée :

- total RDV
- par statut
- par mode de réservation
- par source de création
        """,
        parameters=[
            OpenApiParameter(
                name="annee",
                type=int,
                required=True,
                description="Année (ex: 2026)"
            )
        ],
        responses=RDVStatsParAnneeSerializer
    )
    def get(self, request):

        # ==========================
        # PARAM VALIDATION
        # ==========================
        annee = request.query_params.get("annee")

        if not annee:
            return Response(
                {"detail": "Le paramètre 'annee' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            annee = int(annee)
        except ValueError:
            return Response(
                {"detail": "Année invalide (YYYY)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================
        # QUERYSET
        # ==========================
        rdvs = RDV.objects.filter(date_heure_rdv__year=annee)

        # ==========================
        # TOTAL
        # ==========================
        total_rdv = rdvs.count()

        # ==========================
        # PAR STATUT
        # ==========================
        rdv_par_statut = {
            "En_attente": 0,
            "Confirmer": 0,
            "Annuler": 0,
            "Absent": 0,
            "Terminer": 0,
        }

        for item in rdvs.values("statut_rdv").annotate(total=Count("rdv_id")):
            rdv_par_statut[item["statut_rdv"]] = item["total"]

        # ==========================
        # PAR MODE
        # ==========================
        rdv_par_mode = {
            item["mode_reservation"]: item["total"]
            for item in rdvs.values("mode_reservation").annotate(total=Count("rdv_id"))
        }

        # ==========================
        # PAR SOURCE
        # ==========================
        rdv_par_source = {
            item["source_creation"]: item["total"]
            for item in rdvs.values("source_creation").annotate(total=Count("rdv_id"))
        }

        # ==========================
        # RESPONSE
        # ==========================
        return Response(
            {
                "annee": annee,
                "total_rdv": total_rdv,
                "rdv_par_statut": rdv_par_statut,
                "rdv_par_mode_reservation": rdv_par_mode,
                "rdv_par_source_creation": rdv_par_source,
            },
            status=status.HTTP_200_OK
        )