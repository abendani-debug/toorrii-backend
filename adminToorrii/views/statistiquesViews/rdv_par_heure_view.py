from django.db.models import Count, Q
from django.db.models.functions import ExtractHour
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from adminToorrii.serializers import RDVStatsParHeureSerializer
from adminToorrii.permissions import IsAdminUserCustom


class RDVStatsParHeureView(APIView):
    """
    Endpoint : Statistiques GLOBAL par heure (toutes les dates)

    URL : /api/statistiques/rdv/heure-global/

    ✔ Toutes les dates
    ✔ Tous les services
    ✔ Option : filtrer par heure
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques globales par heure (toutes les dates)",
        parameters=[
            OpenApiParameter(
                name="heure",
                description="Heure spécifique (0-23) (optionnel)",
                required=False,
                type=int
            ),
        ],
        responses={200: RDVStatsParHeureSerializer},
    )
    
    def get(self, request):

        # ===============================
        # 1. Param
        # ===============================
        heure_param = request.query_params.get("heure")

        rdvs = RDV.objects.all()

        # ===============================
        # 2. Filtre heure (optionnel)
        # ===============================
        if heure_param is not None:
            try:
                heure_param = int(heure_param)
                if heure_param < 0 or heure_param > 23:
                    raise ValueError
                rdvs = rdvs.filter(date_heure_rdv__hour=heure_param)
            except ValueError:
                return Response(
                    {"error": "Le paramètre 'heure' doit être entre 0 et 23."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ===============================
        # 3. Agrégation
        # ===============================
        stats_queryset = (
            rdvs.annotate(heure=ExtractHour("date_heure_rdv"))
            .values("heure")
            .annotate(
                total=Count("rdv_id"),
                confirmes=Count("rdv_id", filter=Q(statut_rdv="Confirmer")),
                en_attente=Count("rdv_id", filter=Q(statut_rdv="En_attente")),
                annules=Count("rdv_id", filter=Q(statut_rdv="Annuler")),
                terminer=Count("rdv_id", filter=Q(statut_rdv="Terminer")),
                absent=Count("rdv_id", filter=Q(statut_rdv="Absent")),
            )
            .order_by("heure")
        )

        # ===============================
        # 4. Formatage
        # ===============================
        stats_par_heure = [
            {
                "heure": f"{item['heure']:02d}:00",
                "total": item["total"],
                "confirmes": item["confirmes"],
                "en_attente": item["en_attente"],
                "annules": item["annules"],
                "terminer": item["terminer"],
                "absent": item["absent"],
            }
            for item in stats_queryset
        ]

        # ===============================
        # 5. Response
        # ===============================
        response_data = {
            "stats_par_heure": stats_par_heure
        }

        serializer = RDVStatsParHeureSerializer(instance=response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)