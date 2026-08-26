from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import (
    RDVStatsParMoisSerializer,
    ErrorSerializer
)


class RDVStatsParMoisView(APIView):
    """
    Statistiques RDV par mois (GLOBAL)
    """

    permission_classes = [IsAdminUserCustom]

    MOIS_MAP = {
        "janvier": 1,
        "fevrier": 2,
        "février": 2,
        "mars": 3,
        "avril": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "aout": 8,
        "août": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "decembre": 12,
        "décembre": 12,
    }

    @extend_schema(
        tags=["Statistiques"],
        summary=" Statistiques RDV par mois",
        description="""
Retourne les statistiques globales des rendez-vous pour un mois précis.

✔ Tous les services inclus  
✔ Statistiques propres pour dashboard  
✔ Swagger sans additionalProp  

Paramètre :
- mois (obligatoire)
        """,
        parameters=[
            OpenApiParameter(
                name="mois",
                required=True,
                type=str,
                description="Nom du mois (ex: janvier, fevrier, mars)"
            )
        ],
        responses={
            200: RDVStatsParMoisSerializer,
            400: ErrorSerializer   
        }
    )
    def get(self, request):

        # ===============================
        # 1. PARAM
        # ===============================
        mois = request.query_params.get("mois")

        if not mois:
            return Response(
                {"detail": "Le paramètre 'mois' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        mois = mois.strip().lower()

        # ===============================
        # 2. VALIDATION
        # ===============================
        if mois not in self.MOIS_MAP:
            return Response(
                {"detail": "Mois invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        mois_number = self.MOIS_MAP[mois]

        # ===============================
        # 3. QUERY
        # ===============================
        rdvs = RDV.objects.filter(date_heure_rdv__month=mois_number)

        # ===============================
        # 4. STATS STATUT
        # ===============================
        rdv_par_statut = {
            "En_attente": 0,
            "Confirmer": 0,
            "Annuler": 0,
            "Absent": 0,
            "Terminer": 0,
        }

        for item in rdvs.values("statut_rdv").annotate(count=Count("rdv_id")):
            rdv_par_statut[item["statut_rdv"]] = item["count"]

        # ===============================
        # 5. MODE RESERVATION
        # ===============================
        rdv_par_mode_reservation = {
            "RDV": 0,
            "File_attente": 0,
        }

        for item in rdvs.values("mode_reservation").annotate(count=Count("rdv_id")):
            rdv_par_mode_reservation[item["mode_reservation"]] = item["count"]

        # ===============================
        # 6. SOURCE CREATION
        # ===============================
        rdv_par_source_creation = {
            "Admin": 0,
            "Client": 0,
        }

        for item in rdvs.values("source_creation").annotate(count=Count("rdv_id")):
            rdv_par_source_creation[item["source_creation"]] = item["count"]

        # ===============================
        # 7. RESPONSE
        # ===============================
        data = {
            "mois": mois,
            "mois_numero": mois_number,
            "total_rdv": rdvs.count(),
            "rdv_par_statut": rdv_par_statut,
            "rdv_par_mode_reservation": rdv_par_mode_reservation,
            "rdv_par_source_creation": rdv_par_source_creation,
        }

        serializer = RDVStatsParMoisSerializer(instance=data)
        return Response(serializer.data, status=status.HTTP_200_OK)