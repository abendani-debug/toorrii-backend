from django.db.models import Count
from django.db.models.functions import ExtractWeekDay

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVStatsParJourResponseSerializer


class RDVStatsParJourSemaineView(APIView):

    permission_classes = [IsAdminUserCustom]

    JOURS_MAP = {
        "dimanche": 1,
        "lundi": 2,
        "mardi": 3,
        "mercredi": 4,
        "jeudi": 5,
        "vendredi": 6,
        "samedi": 7,
    }

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques des RDV par jour de la semaine",

        description="""
Retourne les statistiques des rendez-vous filtrés par jour de la semaine.

### Données retournées :
- total des RDV
- répartition par statut
- répartition par mode de réservation
- répartition par source de création
""",

        parameters=[
            OpenApiParameter(
                name="jour",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="lundi, mardi, mercredi, jeudi, vendredi, samedi, dimanche"
            )
        ],

        responses={
            200: RDVStatsParJourResponseSerializer  # ✔ Swagger propre
        }
    )
    def get(self, request):

        jour = request.query_params.get("jour")

        if not jour:
            return Response(
                {"detail": "Le paramètre 'jour' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        jour = jour.lower().strip()

        if jour not in self.JOURS_MAP:
            return Response(
                {
                    "detail": "Jour invalide.",
                    "valeurs_acceptées": list(self.JOURS_MAP.keys())
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        weekday_number = self.JOURS_MAP[jour]

        rdvs = RDV.objects.annotate(
            weekday=ExtractWeekDay("date_heure_rdv")
        ).filter(weekday=weekday_number)

        total_rdv = rdvs.count()

        # ======================
        # STATUT FIXE
        # ======================
        rdv_par_statut = {
            "En_attente": 0,
            "Confirmer": 0,
            "Annuler": 0,
            "Absent": 0,
            "Terminer": 0,
        }

        for item in rdvs.values("statut_rdv").annotate(count=Count("rdv_id")):
            rdv_par_statut[item["statut_rdv"]] = item["count"]

        # ======================
        # MODE RESERVATION
        # ======================
        rdv_par_mode_reservation = {
            item["mode_reservation"]: item["count"]
            for item in rdvs.values("mode_reservation").annotate(count=Count("rdv_id"))
        }

        # ======================
        # SOURCE CREATION
        # ======================
        rdv_par_source_creation = {
            item["source_creation"]: item["count"]
            for item in rdvs.values("source_creation").annotate(count=Count("rdv_id"))
        }

        return Response(
            {
                "jour": jour,
                "total_rdv": total_rdv,
                "rdv_par_statut": rdv_par_statut,
                "rdv_par_mode_reservation": rdv_par_mode_reservation,
                "rdv_par_source_creation": rdv_par_source_creation,
            },
            status=status.HTTP_200_OK
        )