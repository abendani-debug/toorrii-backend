from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import Professionnel, Service
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreServicesParProfessionnelSerializer


class NombreServicesParProView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre de services par professionnel",
        description="Retourne le nombre total de services associés à un professionnel.",
        parameters=[
            OpenApiParameter(
                name="professionnel_id",
                type=str,
                required=True,
                description="ID du professionnel (ex: pro_1)"
            )
        ],
        responses=NombreServicesParProfessionnelSerializer
    )
    def get(self, request, professionnel_id):

        # ==========================
        # GET PROFESSIONNEL
        # ==========================
        try:
            pro = Professionnel.objects.get(
                professionnel_id=professionnel_id
            )
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Professionnel non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ==========================
        # COUNT SERVICES
        # ==========================
        total_services = Service.objects.filter(
            professionnel=pro
        ).count()

        # ==========================
        # RESPONSE
        # ==========================
        return Response(
            {
                "professionnel_id": professionnel_id,
                "total_services": total_services
            },
            status=status.HTTP_200_OK
        )