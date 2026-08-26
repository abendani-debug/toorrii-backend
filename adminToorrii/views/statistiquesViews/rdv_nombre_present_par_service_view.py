from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse

from adminToorrii.models import RDV, Service
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVNombrePresentParServiceSerializer


class RDVNombrePresentParServiceView(APIView):
    """
    Endpoint : Nombre total des clients présents par service
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre total des clients présents par service",
        description="Retourne le nombre total des RDV avec statut 'Terminer' pour un service donné.",
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                required=True,
                description="Identifiant du service",
                location=OpenApiParameter.PATH,
            )
        ],
        responses={200: RDVNombrePresentParServiceSerializer},
        examples=[
            OpenApiExample(
                "Exemple",
                value={
                    "service_id": "SER_1",
                    "service_nom": "Consultation",
                    "nombre_clients_presents": 25
                }
            )
        ],
    )
    def get(self, request, service_id):

        try:
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist:
            return Response(
                {"detail": "Service non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        nombre_presents = RDV.objects.filter(
            service=service,
            statut_rdv="Terminer"
        ).count()

        data = {
            "service_id": service.service_id,
            "service_nom": service.nom_service,
            "nombre_clients_presents": nombre_presents
        }

        serializer = RDVNombrePresentParServiceSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)