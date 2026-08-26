from django.db import transaction
from django.utils import timezone
import datetime

from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from adminToorrii.models import Ticket, Service, Professionnel
from adminToorrii.permissions import IsProfessionnelUserCustom


class DirectionSerializer(drf_serializers.Serializer):
    """
    Accepte soit :
      - direction = "avancer" | "reculer"  (interface frontend)
      - nouvelle_position = <int>           (interface legacy)
    """
    direction = drf_serializers.ChoiceField(
        choices=["avancer", "reculer"],
        required=False,
        allow_null=True
    )
    nouvelle_position = drf_serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True
    )

    def validate(self, attrs):
        if not attrs.get("direction") and not attrs.get("nouvelle_position"):
            raise drf_serializers.ValidationError(
                "Fournissez 'direction' (avancer/reculer) ou 'nouvelle_position'."
            )
        return attrs


class ModifierPositionClientFileView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @transaction.atomic
    def post(self, request, service_id, ticket_id):

        user = request.user

        # 1. professionnel
        try:
            professionnel = user.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        if professionnel.nombre_priorite <= 0:
            return Response(
                {"error": "Plus de priorité disponible (limite mensuelle atteinte)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. service
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

        # 3. validation input
        serializer = DirectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 4. ticket
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
        except Exception as e:
            return Response(
                {"error": f"Erreur serveur: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        file = ticket.file_attente

        # 5. lock full file
        tickets = list(
            Ticket.objects.select_for_update().filter(
                file_attente=file,
                est_actif_dans_file=True
            ).order_by("position")
        )

        max_pos = len(tickets)
        current_pos = ticket.position  # position 1-indexed

        if current_pos is None:
            return Response(
                {"error": "Ce ticket n'a pas de position valide"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 6. Calculer la nouvelle position
        direction = data.get("direction")
        if direction:
            if direction == "avancer":
                new_pos = current_pos - 1
            else:  # reculer
                new_pos = current_pos + 1

            if new_pos < 1 or new_pos > max_pos:
                return Response(
                    {"error": f"Position limite atteinte (position actuelle: {current_pos})"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            new_pos = data["nouvelle_position"]
            if not (1 <= new_pos <= max_pos):
                return Response(
                    {"error": "Position invalide"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 7. reorder in memory
        tickets.remove(ticket)
        tickets.insert(new_pos - 1, ticket)

        # ============================
        #  FIX CRITIQUE ANTI-CONFLIT
        # ============================

        # STEP 1: move everything OUT of constraint range
        for i, t in enumerate(tickets):
            t.position = 100000 + i
        Ticket.objects.bulk_update(tickets, ["position"])

        # STEP 2: assign final positions
        duree = file.service.duree_moyenne_creneau
        now = timezone.now()

        for i, t in enumerate(tickets, start=1):
            t.position = i
            t.creneau_prevue = now + datetime.timedelta(minutes=duree * (i - 1))

        Ticket.objects.bulk_update(tickets, ["position", "creneau_prevue"])

        # 8. priority
        professionnel.nombre_priorite -= 1
        professionnel.save(update_fields=["nombre_priorite"])

        return Response(
            {
                "message": "Position modifiée avec succès",
                "ticket_id": ticket_id,
                "service_id": service_id,
                "nouvelle_position": new_pos,
                "priorite_restante": professionnel.nombre_priorite
            },
            status=status.HTTP_200_OK
        )
