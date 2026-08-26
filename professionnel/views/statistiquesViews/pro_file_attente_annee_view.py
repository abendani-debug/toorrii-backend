from django.db.models import Count, Sum, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import FileDattente
from professionnel.serializers import ProFileAttenteStatsParAnneeSerializer


class ProFileAttenteStatsParAnneeView(APIView):
    """
    Statistiques des files d'attente par année (professionnel connecté)
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Files d'attente par année",
        description="Retourne les statistiques des files d'attente du professionnel pour une année donnée.",
        parameters=[
            OpenApiParameter(
                name="annee",
                description="Année (ex: 2026)",
                required=True,
                type=int
            )
        ],
        responses=ProFileAttenteStatsParAnneeSerializer
    )
    def get(self, request):

        pro = request.user.professionnel
        annee = request.query_params.get("annee")

        if not annee:
            return Response(
                {"detail": "Le paramètre 'annee' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            annee = int(annee)
        except ValueError:
            return Response(
                {"detail": "Année invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Query optimisée
        files = FileDattente.objects.filter(
            service__professionnel=pro,
            date_jour__year=annee
        )

        stats = {
            "annee": annee,
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

        serializer = ProFileAttenteStatsParAnneeSerializer(stats)

        return Response(serializer.data, status=status.HTTP_200_OK)