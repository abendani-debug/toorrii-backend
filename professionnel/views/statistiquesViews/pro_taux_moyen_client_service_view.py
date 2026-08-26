from django.db.models import Count, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import FileDattente
from professionnel.serializers import ProTauxMoyenClientsParServiceSerializer


class ProTauxMoyenClientsParServiceView(APIView):
    """
    Taux moyen de clients dans les files d'attente par service
    (professionnel connecté)
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="Taux moyen de clients par service",
        description="Retourne le nombre moyen de clients dans les files d'attente pour chaque service du professionnel.",
        responses=ProTauxMoyenClientsParServiceSerializer(many=True)
    )
    def get(self, request):

        pro = request.user.professionnel

        qs = (
            FileDattente.objects
            .filter(service__professionnel=pro)
            .values("service__service_id", "service__nom_service")
            .annotate(
                nombre_files=Count("file_id"),
                total_clients=Sum("nombre_clients")
            )
        )

        result = []

        for item in qs:
            total_files = item["nombre_files"] or 0
            total_clients = item["total_clients"] or 0

            taux_moyen = total_clients / total_files if total_files > 0 else 0

            result.append({
                "service_id": item["service__service_id"],
                "service_nom": item["service__nom_service"],
                "nombre_files": total_files,
                "total_clients": total_clients,
                "taux_moyen_clients": round(taux_moyen, 2),
            })

        serializer = ProTauxMoyenClientsParServiceSerializer(result, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)