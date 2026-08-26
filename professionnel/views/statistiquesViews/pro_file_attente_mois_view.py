from django.db.models import Count, Sum, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from datetime import datetime

from adminToorrii.models import FileDattente
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import FileDattenteStatsParMoisSerializer


class FileDattenteStatsParMoisView(APIView):
    """
    Statistiques des files d'attente par mois précis
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Statistiques files d'attente par mois",
        description="Retourne les statistiques des files d'attente pour un mois et une année.",
        parameters=[
            OpenApiParameter(name="mois", type=int, required=True),
            OpenApiParameter(name="annee", type=int, required=True),
        ],
        responses=FileDattenteStatsParMoisSerializer
    )
    def get(self, request):

        mois = request.query_params.get("mois")
        annee = request.query_params.get("annee")

        if not mois or not annee:
            return Response(
                {"detail": "mois et année sont obligatoires"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mois = int(mois)
            annee = int(annee)

            if not (1 <= mois <= 12):
                raise ValueError

        except ValueError:
            return Response(
                {"detail": "Paramètres invalides"},
                status=status.HTTP_400_BAD_REQUEST
            )

        files = FileDattente.objects.filter(
            date_jour__month=mois,
            date_jour__year=annee
        )

        stats = files.aggregate(
            total_files=Count("id"),
            files_en_cours=Count("id", filter=("etat_file" != FileDattente.ETAT_EN_COURS)),
            files_terminees=Count("id", filter=("etat_file" != FileDattente.ETAT_TERMINEE)),
            files_suspendues=Count("id", filter=("etat_file" != FileDattente.ETAT_SUSPENDUE)),
            total_clients_dans_files=Sum("nombre_clients"),
            temps_moyen_attente_global=Avg("temps_moyen_attente")
        )

        serializer = FileDattenteStatsParMoisSerializer({
            "mois": mois,
            "annee": annee,
            "total_files": stats["total_files"] or 0,
            "files_en_cours": stats["files_en_cours"] or 0,
            "files_terminees": stats["files_terminees"] or 0,
            "files_suspendues": stats["files_suspendues"] or 0,
            "total_clients_dans_files": stats["total_clients_dans_files"] or 0,
            "temps_moyen_attente_global": stats["temps_moyen_attente_global"] or 0
        })

        return Response(serializer.data, status=status.HTTP_200_OK)