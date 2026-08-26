import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from adminToorrii.models import Client
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import NombreClientsSerializer

logger = logging.getLogger(__name__)


class NombreClientView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre total de clients",
        description="""
Endpoint admin pour récupérer les statistiques des clients :

 - total clients  
 - clients actifs  
 - clients inactifs  
        """,
        responses=NombreClientsSerializer
    )
    def get(self, request):

        try:
            total_clients = Client.objects.count()
            clients_actifs = Client.objects.filter(actif=True).count()
            clients_inactifs = Client.objects.filter(actif=False).count()

            data = {
                "total_clients": total_clients,
                "clients_actifs": clients_actifs,
                "clients_inactifs": clients_inactifs,
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                "Erreur récupération clients | %s",
                str(e),
                exc_info=True
            )

            return Response(
                {"detail": "Erreur interne serveur"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )