from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from django.db.models import Q, Avg

from adminToorrii.models import FileDattente, Ticket
from adminToorrii.permissions import IsAdminUserCustom

from adminToorrii.serializers import FileDattenteStatsParAnneeSerializer


class FileDattenteStatsParAnneeView(APIView):
    """
    Statistiques des files d'attente par année
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques des files d’attente par année",
        description="""
Retourne les statistiques des files d’attente pour une année donnée.

 Données :
- Files d'attente
- Clients (tickets hors annulés)
- Temps moyen d'attente
        """,
        parameters=[
            OpenApiParameter(
                name="annee",
                description="Année (ex: 2024)",
                required=True,
                type=int
            )
        ],
        responses=FileDattenteStatsParAnneeSerializer,
        examples=[
            OpenApiExample(
                name="Exemple réponse",
                value={
                    "annee": 2024,
                    "total_files": 120,
                    "files_en_cours": 70,
                    "files_terminees": 40,
                    "files_suspendues": 10,
                    "total_clients_dans_files": 1850,
                    "temps_moyen_attente": 18.5
                }
            )
        ]
    )
    def get(self, request):

        # ==========================
        # PARAM ANNEE
        # ==========================
        annee_str = request.query_params.get("annee")

        if not annee_str:
            return Response(
                {"detail": "Le paramètre 'annee' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            annee = int(annee_str)
        except ValueError:
            return Response(
                {"detail": "Le paramètre 'annee' doit être un entier valide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ==========================
        # FILES
        # ==========================
        files_annee = FileDattente.objects.filter(
            date_creation__year=annee
        )

        # ==========================
        # STATS FILES
        # ==========================
        total_files = files_annee.count()

        files_en_cours = files_annee.filter(
            etat_file=FileDattente.ETAT_EN_COURS
        ).count()

        files_terminees = files_annee.filter(
            etat_file=FileDattente.ETAT_TERMINEE
        ).count()

        files_suspendues = files_annee.filter(
            etat_file=FileDattente.ETAT_SUSPENDUE
        ).count()

        # ==========================
        # CLIENTS (TICKETS)
        # ==========================
        total_clients = Ticket.objects.filter(
            file_attente__date_creation__year=annee
        ).exclude(
            etat_ticket=Ticket.EtatTicket.ANNULER
        ).count()

        # ==========================
        # TEMPS MOYEN ATTENTE
        # ==========================
        temps_moyen = files_annee.aggregate(
            avg=Avg("temps_moyen_attente")
        )["avg"] or 0

        # ==========================
        # RESPONSE
        # ==========================
        data = {
            "annee": annee,
            "total_files": total_files,
            "files_en_cours": files_en_cours,
            "files_terminees": files_terminees,
            "files_suspendues": files_suspendues,
            "total_clients_dans_files": total_clients,
            "temps_moyen_attente": round(temps_moyen, 2)
        }

        serializer = FileDattenteStatsParAnneeSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)