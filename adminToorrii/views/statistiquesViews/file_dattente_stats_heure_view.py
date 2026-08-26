from datetime import datetime

from django.db.models import Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import FileDattente, Ticket
from adminToorrii.permissions import IsAdminUserCustom

from adminToorrii.serializers import FileDattenteStatistiquesSerializer
from adminToorrii.serializers import FileDattenteStatsParHeureSerializer


class FileDattenteStatsParHeureView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Stats files d'attente par heure",
        parameters=[
            OpenApiParameter("heure", str, required=True),
        ],
        responses=FileDattenteStatsParHeureSerializer
    )
    def get(self, request):

        heure_str = request.query_params.get("heure")

        heure_obj = int(heure_str.split(":")[0])

        # ==========================
        # BASE QUERY
        # ==========================
        files_base = FileDattente.objects.all()

        # ==========================
        # STATS EXACTES
        # ==========================
        files_exact = files_base.filter(date_creation__hour=heure_obj)

        stats_exactes = {
            "total_files": files_exact.count(),
            "files_en_cours": files_exact.filter(etat_file=FileDattente.ETAT_EN_COURS).count(),
            "files_terminees": files_exact.filter(etat_file=FileDattente.ETAT_TERMINEE).count(),
            "files_suspendues": files_exact.filter(etat_file=FileDattente.ETAT_SUSPENDUE).count(),
            "total_clients_dans_files": Ticket.objects.filter(
                file_attente__date_creation__hour=heure_obj
            ).exclude(
                etat_ticket=Ticket.EtatTicket.ANNULER
            ).count(),
            "temps_moyen_attente_global": files_exact.aggregate(
                avg=Avg("temps_moyen_attente")
            )["avg"] or 0
        }


        # ==========================
        # RESPONSE
        # ==========================
        data = {
            "heure": heure_obj,
            "stats_exactes": stats_exactes,
        }

        serializer = FileDattenteStatsParHeureSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)