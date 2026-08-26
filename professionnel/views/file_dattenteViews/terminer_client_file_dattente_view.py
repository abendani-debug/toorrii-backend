from django.db import transaction
from django.utils import timezone
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse
)

from adminToorrii.models import (
    Ticket,
    Service,
    Professionnel
)
from adminToorrii.permissions import IsProfessionnelUserCustom


class TerminerClientFileAttenteView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["File d'attente Professionnel"],
        summary="Déclarer un ticket comme terminé",
        description="""
Permet au professionnel de marquer un ticket comme terminé.

### Effets :
- ticket.etat_ticket → UTILISER
- ticket.est_actif_dans_file → False
- ticket.position → NULL
- Recalcul complet de la file restante
- Mise à jour des créneaux
- Décrément du compteur de file (nombre_clients)
""",
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            ),
            OpenApiParameter(
                name="ticket_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Ticket terminé avec succès",
                response={
                    "example": {
                        "message": "Ticket terminé avec succès",
                        "ticket_id": "TKT_1",
                        "service_id": "SER_1"
                    }
                }
            )
        }
    )
    @transaction.atomic
    def post(self, request, service_id, ticket_id):

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
        try:
            ticket = Ticket.objects.select_for_update().get(
                ticket_id=ticket_id,
                file_attente__service=service,
                file_attente__date_jour=timezone.now().date(),
                est_actif_dans_file=True
            )
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Ticket introuvable dans cette file"},
                status=status.HTTP_404_NOT_FOUND
            )

        file = ticket.file_attente

        # =========================
        # 4. TERMINER LE TICKET
        # position=None libère la contrainte unique (file_attente_id, position)
        # =========================
        ticket.etat_ticket = Ticket.EtatTicket.UTILISER
        ticket.est_actif_dans_file = False
        ticket.position = None
        ticket.date_validation = timezone.now()
        ticket.save(update_fields=[
            "etat_ticket",
            "est_actif_dans_file",
            "position",
            "date_validation"
        ])

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
                "message": "Ticket terminé avec succès",
                "ticket_id": ticket_id,
                "service_id": service_id
            },
            status=status.HTTP_200_OK
        )