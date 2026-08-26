from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from django.db.models import Q

from adminToorrii.models import FileDattente, Ticket


class FileDattenteStatsParMoisView(APIView):

    @extend_schema(
        tags=["Statistiques"],
        summary="Stats files d'attente par mois",
        description="""
Retourne les statistiques des files d’attente pour un mois donné.

 Les clients sont calculés via les tickets (hors annulés)
        """,
        parameters=[
            OpenApiParameter(
                name="mois",
                type=int,
                required=True,
                description="1 = Janvier ... 12 = Décembre"
            )
        ],
        responses=dict,
        examples=[
            OpenApiExample(
                name="Exemple réponse",
                value={
                    "mois": 3,
                    "total_files": 45,
                    "files_en_cours": 30,
                    "files_terminees": 10,
                    "files_suspendues": 5,
                    "total_clients_dans_files": 350
                }
            )
        ]
    )
    def get(self, request):

        # ==========================
        # PARAM
        # ==========================
        mois_str = request.query_params.get("mois")

        if not mois_str:
            return Response(
                {"detail": "Le paramètre 'mois' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mois = int(mois_str)
            if not (1 <= mois <= 12):
                raise ValueError
        except ValueError:
            return Response(
                {"detail": "mois doit être entre 1 et 12"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================
        # FILES
        # ==========================
        files = FileDattente.objects.filter(
            date_jour__month=mois
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
        # CLIENTS (TICKETS - SOURCE UNIQUE)
        # ==========================
        total_clients = Ticket.objects.filter(
            file_attente__date_jour__month=mois
        ).exclude(
            etat_ticket=Ticket.EtatTicket.ANNULER
        ).count()

        # ==========================
        # RESPONSE
        # ==========================
        data = {
            "mois": mois,
            "total_files": total_files,
            "files_en_cours": files_en_cours,
            "files_terminees": files_terminees,
            "files_suspendues": files_suspendues,
            "total_clients_dans_files": total_clients
        }

        return Response(data, status=status.HTTP_200_OK)