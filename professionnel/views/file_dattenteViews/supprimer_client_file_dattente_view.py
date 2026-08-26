from django.db import transaction
from django.utils import timezone
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from adminToorrii.models import (
    Ticket,
    Service,
    Professionnel
)
from adminToorrii.permissions import IsProfessionnelUserCustom


class SupprimerClientFileAttenteView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["File d'attente Professionnel"],
        summary="Supprimer un client de la file d'attente",
        description="""
Permet au professionnel de retirer un client de la file d'attente d'un service.

### 🔐 Conditions :
- Le service doit appartenir au professionnel
- Le ticket doit être actif dans la file du jour

### ⚙️ Fonctionnement :
1. Vérification du professionnel
2. Vérification du service
3. Récupération du ticket actif
4. Annulation du ticket (soft delete + position libérée)
5. Recalcul complet de la file
6. Mise à jour des créneaux
7. Mise à jour du nombre de clients

### ⚠️ Technique :
- transaction.atomic
- select_for_update (anti-concurrence)
- OFFSET pour éviter les conflits DB
- update séquentiel (PAS de bulk_update)
""",

        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du service (ex: SER_1)"
            ),
            OpenApiParameter(
                name="ticket_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du ticket (ex: TKT_10)"
            )
        ],

        responses={
            200: OpenApiResponse(
                description="Client supprimé avec succès",
                response={
                    "type": "object",
                    "example": {
                        "message": "Client supprimé de la file avec succès",
                        "service_id": "SER_1",
                        "ticket_id": "TKT_10",
                        "nombre_clients_restant": 4
                    }
                }
            ),
            404: OpenApiResponse(
                description="Ticket introuvable",
                response={
                    "example": {
                        "error": "Client non trouvé dans cette file"
                    }
                }
            ),
            400: OpenApiResponse(
                description="Erreur métier",
                response={
                    "example": {
                        "error": "Impossible de modifier une ancienne file d'attente"
                    }
                }
            )
        },

        examples=[
            OpenApiExample(
                "Succès",
                value={
                    "message": "Client supprimé de la file avec succès",
                    "service_id": "SER_1",
                    "ticket_id": "TKT_10",
                    "nombre_clients_restant": 4
                },
                response_only=True
            )
        ]
    )

    @transaction.atomic
    def delete(self, request, service_id, ticket_id):

        user = request.user

        # =========================
        # 1. PROFESSIONNEL
        # =========================
        try:
            professionnel = user.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # =========================
        # 2. SERVICE
        # =========================
        try:
            service = Service.objects.get(
                service_id=service_id,
                professionnel=professionnel
            )
        except Service.DoesNotExist:
            return Response(
                {"error": "Service introuvable ou non autorisé"},
                status=status.HTTP_404_NOT_FOUND
            )

        # =========================
        # 3. TICKET
        # =========================
        ticket = Ticket.objects.select_for_update().filter(
            ticket_id=ticket_id,
            file_attente__service=service,
            file_attente__date_jour=timezone.now().date(),
            est_actif_dans_file=True
        ).first()

        if not ticket:
            return Response(
                {"error": "Client non trouvé dans cette file"},
                status=status.HTTP_404_NOT_FOUND
            )

        file = ticket.file_attente

        # empêcher modification ancienne file
        if file.date_jour != timezone.now().date():
            return Response(
                {"error": "Impossible de modifier une ancienne file d'attente"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # =========================
        # 4. SOFT DELETE
        # position=None libère la contrainte unique (file_attente_id, position)
        # pour que le recalcul puisse réassigner les positions 1, 2, 3...
        # sans conflit avec ce ticket annulé
        # =========================
        ticket.etat_ticket = Ticket.EtatTicket.ANNULER
        ticket.est_actif_dans_file = False
        ticket.position = None  
        ticket.save(update_fields=["etat_ticket", "est_actif_dans_file", "position"])

        # =========================
        # 5. RÉCUPÉRER FILE ACTIVE (LOCK)
        # =========================
        tickets = list(
            Ticket.objects.select_for_update().filter(
                file_attente=file,
                est_actif_dans_file=True
            ).order_by("position")
        )

        # =========================
        # 6. PHASE 1 : OFFSET SAFE
        # =========================
        OFFSET = len(tickets) + 100

        for i, t in enumerate(tickets):
            t.position = OFFSET + i
            t.save(update_fields=["position"])

        # =========================
        # 7. PHASE 2 : POSITION FINALE
        # =========================
        duree = file.service.duree_moyenne_creneau
        now = timezone.now()

        for i, t in enumerate(tickets, start=1):
            t.position = i
            t.creneau_prevue = now + datetime.timedelta(minutes=duree * (i - 1))
            t.save(update_fields=["position", "creneau_prevue"])

        # =========================
        # 8. UPDATE FILE
        # =========================
        file.nombre_clients = len(tickets)
        file.save(update_fields=["nombre_clients"])

        # =========================
        # 9. RESPONSE
        # =========================
        return Response(
            {
                "message": "Client supprimé de la file avec succès",
                "service_id": service_id,
                "ticket_id": ticket_id,
                "nombre_clients_restant": file.nombre_clients
            },
            status=status.HTTP_200_OK
        )