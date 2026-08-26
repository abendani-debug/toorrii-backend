from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Client
from adminToorrii.serializers import AfficherClientSerializer

logger = logging.getLogger(__name__)

class AfficherClientView(APIView):
    """
    Endpoint ADMIN pour afficher tous les clients avec tous les champs
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Client"],
        summary="Lister tous les clients (tous les champs)",
        description="""
Permet à un **administrateur** de consulter **tous les clients**
avec **tous les champs** inclus (id, nom, prénom, email, token, numéro, date inscription, actif...).

### Sécurité :
- Accès réservé aux administrateurs
""",
        responses={
            200: OpenApiResponse(
                description="Liste des clients récupérée avec succès",
                response=AfficherClientSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "status": True,
                            "total_clients": 2,
                            "clients": [
                                {
                                    "id_client": "CLN_1",
                                    "token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                                    "nom": "Ali",
                                    "prenom": "Yacine",
                                    "email": "ali@test.com",
                                    "numero_telephone": "+213661000000",
                                    "date_inscription": "2025-12-10T09:00:00Z",
                                    "actif": True
                                }
                            ]
                        }
                    )
                ],
            ),
            403: OpenApiResponse(
                description="Accès interdit",
                examples=[
                    OpenApiExample(
                        "Non autorisé",
                        value={
                            "status": False,
                            "error": "Accès refusé. Droits administrateur requis."
                        }
                    )
                ],
            ),
            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        "Erreur interne",
                        value={
                            "status": False,
                            "error": "Erreur interne lors de la récupération des clients."
                        }
                    )
                ],
            ),
        },
    )
    def get(self, request):
        try:
            clients = Client.objects.all().order_by("-date_inscription")
            serializer = AfficherClientSerializer(clients, many=True)

            return Response(
                {
                    "status": True,
                    "total_clients": clients.count(),
                    "clients": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(
                "Erreur ListeClientsAdminFullView | %s",
                str(e),
                exc_info=True
            )
            return Response(
                {
                    "status": False,
                    "error": "Erreur interne lors de la récupération des clients."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
