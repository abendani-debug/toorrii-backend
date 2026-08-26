from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from adminToorrii.models import FileDattente, Ticket


class FileDattenteStatsParJourView(APIView):

    @extend_schema(
        tags=["Statistiques"],
        summary="Stats files d'attente par jour de la semaine",
        description="""
Retourne les statistiques des files d'attente pour un jour donné.

 Clients calculés via tickets (hors annulés)
        """,
        parameters=[
            OpenApiParameter(
                name="jour",
                type=str,
                required=True,
                description="Dimanche, Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi"
            )
        ],
        responses=dict,
        examples=[
            OpenApiExample(
                name="Exemple réponse",
                value={
                    "jour": "Lundi",
                    "total_files": 10,
                    "files_en_cours": 6,
                    "files_terminees": 3,
                    "files_suspendues": 1,
                    "total_clients_dans_files": 120
                }
            )
        ]
    )
    def get(self, request):

        # ==========================
        # PARAM
        # ==========================
        jour_str = request.query_params.get("jour")

        if not jour_str:
            return Response(
                {"detail": "Le paramètre 'jour' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        jour_str = jour_str.strip().capitalize()

        jours_map = {
            "Dimanche": 1,
            "Lundi": 2,
            "Mardi": 3,
            "Mercredi": 4,
            "Jeudi": 5,
            "Vendredi": 6,
            "Samedi": 7
        }

        if jour_str not in jours_map:
            return Response(
                {"detail": "Jour invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        week_day = jours_map[jour_str]

        # ==========================
        # FILES
        # ==========================
        files = FileDattente.objects.filter(
            date_jour__week_day=week_day
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
            file_attente__date_jour__week_day=week_day
        ).exclude(
            etat_ticket=Ticket.EtatTicket.ANNULER
        ).count()

        # ==========================
        # RESPONSE
        # ==========================
        data = {
            "jour": jour_str,
            "total_files": total_files,
            "files_en_cours": files_en_cours,
            "files_terminees": files_terminees,
            "files_suspendues": files_suspendues,
            "total_clients_dans_files": total_clients
        }

        return Response(data, status=status.HTTP_200_OK)