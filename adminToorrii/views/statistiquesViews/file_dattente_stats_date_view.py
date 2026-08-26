from datetime import datetime

from django.db.models import Count, Q, Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from adminToorrii.models import FileDattente, Ticket
from adminToorrii.permissions import IsAdminUserCustom

from adminToorrii.serializers import FileDattenteStatsParDateSerializer


class FileDattenteStatsParDateView(APIView):
    """
    Statistiques des files d'attente par date
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques des files d’attente par date",
        description="""
Retourne les statistiques des files d’attente pour une date donnée.

 Données :
- Files d’attente du jour
- Clients calculés via tickets (hors annulés)
- Temps moyen d’attente global
        """,
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                required=True,
                description="Date au format YYYY-MM-DD"
            )
        ],
        responses=FileDattenteStatsParDateSerializer,
        examples=[
            OpenApiExample(
                name="Exemple réponse",
                value={
                    "date": "2026-03-05",
                    "total_files": 5,
                    "files_en_cours": 2,
                    "files_terminees": 2,
                    "files_suspendues": 1,
                    "total_clients_dans_files": 48,
                    "temps_moyen_attente_global": 20.5
                }
            )
        ]
    )
    def get(self, request):

        # ==========================
        # VALIDATION DATE
        # ==========================
        date_str = request.query_params.get("date")

        if not date_str:
            return Response(
                {"detail": "Le paramètre 'date' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Format de date invalide (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================
        # FILES DU JOUR
        # ==========================
        files = FileDattente.objects.filter(date_jour=date_obj)

        # ==========================
        # STATS FILES
        # ==========================
        total_files = files.count()

        files_en_cours = files.filter(
            etat_file=FileDattente.ETAT_EN_COURS
        ).count()

        files_terminees = files.filter(
            etat_file=FileDattente.ETAT_TERMINEE
        ).count()

        files_suspendues = files.filter(
            etat_file=FileDattente.ETAT_SUSPENDUE
        ).count()

        # ==========================
        # CLIENTS VIA TICKETS (IMPORTANT)
        # ==========================
        total_clients = Ticket.objects.filter(
            file_attente__date_jour=date_obj
        ).exclude(
            etat_ticket=Ticket.EtatTicket.ANNULER
        ).count()

        # ==========================
        # TEMPS MOYEN ATTENTE
        # ==========================
        temps_moyen = files.aggregate(
            avg=Avg("temps_moyen_attente")
        )["avg"] or 0

        # ==========================
        # RESPONSE
        # ==========================
        data = {
            "date": date_obj,
            "total_files": total_files,
            "files_en_cours": files_en_cours,
            "files_terminees": files_terminees,
            "files_suspendues": files_suspendues,
            "total_clients_dans_files": total_clients,
            "temps_moyen_attente_global": round(temps_moyen, 2)
        }

        serializer = FileDattenteStatsParDateSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)