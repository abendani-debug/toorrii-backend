from django.db.models import Count, Avg, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import FileDattente, Ticket
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import FileDattenteStatistiquesSerializer


class FileDattenteStatistiquesView(APIView):
    """
    Endpoint : Statistiques globales des files d’attente
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques globales des files d’attente",
        description="""
Retourne les statistiques globales des files d’attente.

✔ Total files
✔ Répartition par état
✔ Clients calculés via tickets (hors annulés)
✔ Temps moyen d’attente global
        """,
        responses=FileDattenteStatistiquesSerializer
    )
    def get(self, request):

        # ==========================
        # STATS FILES (1 requête)
        # ==========================
        stats = FileDattente.objects.aggregate(
            total_files=Count("file_id"),
            files_en_cours=Count("file_id", filter=Q(etat_file=FileDattente.ETAT_EN_COURS)),
            files_terminees=Count("file_id", filter=Q(etat_file=FileDattente.ETAT_TERMINEE)),
            files_suspendues=Count("file_id", filter=Q(etat_file=FileDattente.ETAT_SUSPENDUE)),
            temps_moyen_attente_global=Avg("temps_moyen_attente"),
        )

        # ==========================
        # CLIENTS VIA TICKETS
        # ==========================
        total_clients = Ticket.objects.exclude(
            etat_ticket=Ticket.EtatTicket.ANNULER
        ).count()

        # ==========================
        # RESPONSE DATA
        # ==========================
        data = {
            "total_files": stats["total_files"] or 0,
            "files_en_cours": stats["files_en_cours"] or 0,
            "files_terminees": stats["files_terminees"] or 0,
            "files_suspendues": stats["files_suspendues"] or 0,
            "total_clients_dans_files": total_clients,
            "temps_moyen_attente_global": round(stats["temps_moyen_attente_global"] or 0, 2),
        }

        return Response(data, status=status.HTTP_200_OK)