from datetime import datetime

from django.db.models import Sum, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import FileDattente
from professionnel.serializers import ProFileAttenteStatsIntervalleSerializer


class ProFileAttenteStatsIntervalleView(APIView):
    """
    Statistiques des files d'attente par intervalle (professionnel connecté)
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Files d'attente par intervalle",
        description="Retourne les statistiques des files d'attente du professionnel sur une période donnée.",
        parameters=[
            OpenApiParameter(name="date_debut", type=str, required=True),
            OpenApiParameter(name="date_fin", type=str, required=True),
        ],
        responses=ProFileAttenteStatsIntervalleSerializer
    )
    def get(self, request):

        pro = request.user.professionnel

        date_debut_str = request.query_params.get("date_debut")
        date_fin_str = request.query_params.get("date_fin")

        if not date_debut_str or not date_fin_str:
            return Response(
                {"detail": "date_debut et date_fin sont obligatoires."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date()
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Format de date invalide (YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if date_debut > date_fin:
            return Response(
                {"detail": "date_debut doit être <= date_fin."},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Query principale optimisée
        files = FileDattente.objects.filter(
            service__professionnel=pro,
            date_jour__date__range=[date_debut, date_fin]
        )

        stats = {
            "date_debut": date_debut,
            "date_fin": date_fin,

            "total_files": files.count(),
            "files_en_cours": files.filter(etat_file=FileDattente.ETAT_EN_COURS).count(),
            "files_terminees": files.filter(etat_file=FileDattente.ETAT_TERMINEE).count(),
            "files_suspendues": files.filter(etat_file=FileDattente.ETAT_SUSPENDUE).count(),

            "total_clients_dans_files": files.aggregate(
                total=Sum("nombre_clients")
            )["total"] or 0,

            "temps_moyen_attente_global": files.aggregate(
                avg=Avg("temps_moyen_attente")
            )["avg"] or 0,
        }

        serializer = ProFileAttenteStatsIntervalleSerializer(stats)

        return Response(serializer.data, status=status.HTTP_200_OK)