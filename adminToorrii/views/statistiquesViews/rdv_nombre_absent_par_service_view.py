from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV, Service
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVNombreAbsentParServiceSerializer


class RDVNombreAbsentParServiceView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre de clients absents par service",
        description="Retourne le nombre de RDV avec statut 'Absent' pour un service donné.",
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                description="Identifiant du service"
            )
        ],
        responses=RDVNombreAbsentParServiceSerializer
    )
    def get(self, request, service_id):

        # ==========================
        # CHECK SERVICE
        # ==========================
        try:
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist:
            return Response(
                {"detail": "Service non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================
        # COUNT ABSENTS
        # ==========================
        nombre_absents = RDV.objects.filter(
            service=service,
            statut_rdv="Absent"
        ).count()

        # ==========================
        # RESPONSE
        # ==========================
        return Response(
            {
                "service_id": service.service_id,
                "service_nom": service.nom_service,
                "nombre_clients_absents": nombre_absents
            },
            status=status.HTTP_200_OK
        )