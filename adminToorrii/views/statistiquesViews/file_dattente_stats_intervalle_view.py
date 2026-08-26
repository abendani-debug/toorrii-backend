from datetime import datetime

from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from adminToorrii.models import FileDattente, Ticket
from adminToorrii.permissions import IsAdminUserCustom


class FileDattenteStatsParIntervalleView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Stats files d'attente par intervalle",
        description="""
Retourne les statistiques des files d’attente sur un intervalle de dates.

 Les clients sont calculés via les tickets (hors annulés)
        """,
        parameters=[
            OpenApiParameter(
                name="date_debut",
                type=str,
                required=True,
                description="YYYY-MM-DD"
            ),
            OpenApiParameter(
                name="date_fin",
                type=str,
                required=True,
                description="YYYY-MM-DD"
            )
        ],
        responses=dict,
        examples=[
            OpenApiExample(
                name="Exemple réponse",
                value={
                    "date_debut": "2026-01-01",
                    "date_fin": "2026-03-05",
                    "total_files": 120,
                    "files_en_cours": 80,
                    "files_terminees": 30,
                    "files_suspendues": 10,
                    "total_clients_dans_files": 950
                }
            )
        ]
    )
    def get(self, request):

        # ==========================
        # PARAMS
        # ==========================
        date_debut_str = request.query_params.get("date_debut")
        date_fin_str = request.query_params.get("date_fin")

        if not date_debut_str or not date_fin_str:
            return Response(
                {"detail": "date_debut et date_fin sont obligatoires"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()

            if date_fin < date_debut:
                raise ValueError("date_fin doit être >= date_debut")

        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================
        # FILES INTERVALLE
        # ==========================
        files = FileDattente.objects.filter(
            date_jour__gte=date_debut,
            date_jour__lte=date_fin
        )

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
            file_attente__date_jour__gte=date_debut,
            file_attente__date_jour__lte=date_fin
        ).exclude(
            etat_ticket=Ticket.EtatTicket.ANNULER
        ).count()

        # ==========================
        # RESPONSE
        # ==========================
        data = {
            "date_debut": date_debut,
            "date_fin": date_fin,
            "total_files": total_files,
            "files_en_cours": files_en_cours,
            "files_terminees": files_terminees,
            "files_suspendues": files_suspendues,
            "total_clients_dans_files": total_clients
        }

        return Response(data, status=status.HTTP_200_OK)