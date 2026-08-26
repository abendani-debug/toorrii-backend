from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter
)

from adminToorrii.models import Ticket, Client
from adminToorrii.permissions import IsAdminUserCustom


class AfficherDetailFileAttenteClientView(APIView):
    """
    Endpoint : Files d'attente d'un client
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["File d'attente"],
        summary="Détail des files d'attente d’un client",
        description="""
Retourne toutes les files d'attente dans lesquelles un client possède des tickets.

 Données retournées :
- Informations du client
- Liste des files d’attente
- Service associé à chaque file
- Tickets du client uniquement

 Structure :
- Groupement par file d’attente
- Tickets filtrés par client

 Accès :
- Réservé aux administrateurs
        """,

        parameters=[
            OpenApiParameter(
                name="client_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID du client (ex: CLN_1)",
                required=True
            )
        ],

        responses={
            200: OpenApiResponse(
                description="Données récupérées avec succès",
                response={
                    "type": "object",
                    "example": {
                        "client": {
                            "client_id": "CLN_1",
                            "client_nom": "Ahmed",
                            "client_prenom": "Benali",
                            "client_numero_telephone": "+213675902494",
                            "client_email": "client@email.com"
                        },
                        "files": [
                            {
                                "file_id": "FILE_1",
                                "date_jour": "2026-03-10",
                                "service": {
                                    "service_id": "SER_1",
                                    "nom_service": "Consultation"
                                },
                                "tickets_client": [
                                    {
                                        "ticket_id": "TKT_12",
                                        "code_ticket": "CTK-0012",
                                        "position": 3,
                                        "creneau_prevue": "2026-03-10T10:30:00",
                                        "etat_ticket": "En_Attente"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),

            404: OpenApiResponse(
                description="Client introuvable",
                response={
                    "type": "object",
                    "example": {
                        "error": "Client avec l'ID CLN_1 non trouvé"
                    }
                }
            )
        },

        examples=[
            OpenApiExample(
                "Exemple requête",
                summary="client_id path param",
                value={"client_id": "CLN_1"},
                request_only=True
            )
        ]
    )

    def get(self, request, client_id):

        # =========================
        # GET CLIENT
        # =========================
        try:
            client = Client.objects.get(id_client=client_id)
        except Client.DoesNotExist:
            return Response(
                {"error": f"Client avec l'ID {client_id} non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        # =========================
        # GET TICKETS
        # =========================
        tickets = Ticket.objects.filter(
            client=client
        ).select_related(
            "file_attente",
            "file_attente__service",
            "file_attente__service__professionnel"
        )

        # =========================
        # RESPONSE STRUCTURE
        # =========================
        resultat = {
            "client": {
                "client_id": client.id_client,
                "client_nom": client.nom,
                "client_prenom": client.prenom,
                "client_numero_telephone": str(client.numero_telephone),
                "client_email": client.email
            },
            "files": []
        }

        files_map = {}

        for ticket in tickets:

            file = ticket.file_attente
            file_id = file.file_id

            if file_id not in files_map:
                files_map[file_id] = {
                    "file_id": file_id,
                    "date_jour": file.date_jour,
                    "service": {
                        "service_id": file.service.service_id,
                        "nom_service": file.service.nom_service,
                    },
                    "tickets_client": []
                }

            files_map[file_id]["tickets_client"].append({
                "ticket_id": ticket.ticket_id,
                "code_ticket": ticket.code_ticket,
                "position": ticket.position,
                "creneau_prevue": ticket.creneau_prevue,
                "etat_ticket": ticket.etat_ticket
            })

        resultat["files"] = list(files_map.values())

        return Response(resultat, status=status.HTTP_200_OK)