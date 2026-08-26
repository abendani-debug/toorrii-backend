import datetime
from django.utils import timezone
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter
)

from adminToorrii.models import (
    Service,
    Professionnel,
    FileDattente,
    Ticket,
    Client,
    ServicePlanning
)
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import AjouterClientFileAttenteSerializer
from professionnel.utils.rdv_service import RDVCreationService


class AjouterClientFileAttenteView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["File d'attente Professionnel"],
        summary="Ajouter un client dans la file d’attente (avec validation métier)",
        description="""
Permet à un professionnel d’ajouter un client dans la file d’attente.

###  Vérifications métier (IDENTIQUE RDV) :
- Vérifie le professionnel connecté
- Vérifie que le service lui appartient
- Vérifie les exceptions (jours spéciaux)
- Vérifie le planning (jour de travail)
- Vérifie les horaires du service
- Vérifie les pauses

###  Fonctionnement :
- Création ou récupération de la file du jour
- Calcul automatique de la position
- Calcul du créneau estimé
- Création du ticket FILE_D_ATTENTE
- Mise à jour du nombre de clients

###  Important :
👉 Impossible d’ajouter un client si le service est fermé
""",

        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du service (ex: SER_1)"
            )
        ],

        request=AjouterClientFileAttenteSerializer,

        responses={
            201: OpenApiResponse(
                description="Client ajouté avec succès",
                response={
                    "type": "object",
                    "example": {
                        "message": "Client ajouté dans la file",
                        "ticket": {
                            "ticket_id": "TKT_15",
                            "code_ticket": "CTK-20260417-0005",
                            "position": 3,
                            "creneau_prevue": "2026-04-17T10:30:00+01:00",
                            "etat_ticket": "En_Attente"
                        }
                    }
                }
            ),

            400: OpenApiResponse(
                description="Erreur métier",
                response={
                    "example": {
                        "error": "Service fermé actuellement"
                    }
                }
            ),

            404: OpenApiResponse(
                description="Ressource introuvable",
                response={
                    "example": {
                        "error": "Service introuvable ou non autorisé"
                    }
                }
            )
        },

        examples=[
            OpenApiExample(
                "Exemple requête",
                value={
                    "client_numero_telephone": "+213675902494",
                    "client_nom": "Ali",
                    "client_prenom": "Ahmed",
                    "client_email": "ali@email.com"
                },
                request_only=True
            )
        ]
    )

    @transaction.atomic
    def post(self, request, service_id):

        user = request.user

        # 1 Professionnel
        try:
            professionnel = user.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2 Service
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

        # 3 Validation input
        serializer = AjouterClientFileAttenteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # 4 Création / récupération client
        client, _ = Client.objects.get_or_create(
            numero_telephone=data["client_numero_telephone"],
            defaults={
                "nom": data.get("client_nom"),
                "prenom": data.get("client_prenom"),
                "email": data.get("client_email"),
            }
        )

        now = timezone.now()
        date_res = now.date()
        heure_res = now.time()

        #  5 Vérifications métier (COMME RDV)
        RDVCreationService.check_exception(service, date_res, heure_res)

        nom_jour = RDVCreationService.get_day_name(now)

        planning = ServicePlanning.objects.filter(
            service=service,
            nom_jour=nom_jour
        ).first()

        if not planning:
            return Response(
                {"error": "Service non disponible aujourd’hui"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not (planning.heure_debut_service <= heure_res <= planning.heure_fin_service):
            return Response(
                {"error": "Service fermé actuellement"},
                status=status.HTTP_400_BAD_REQUEST
            )

        RDVCreationService.check_pause(planning, heure_res)

        # 6 File d’attente
        file_dattente, _ = FileDattente.objects.get_or_create(
            service=service,
            professionnel=professionnel,
            date_jour=date_res,
            defaults={
                "temps_moyen_attente": service.duree_moyenne_creneau
            }
        )

        # 7 Position
        position = Ticket.objects.filter(
            file_attente=file_dattente
        ).count() + 1

        # 8 Créneau estimé
        minutes = service.duree_moyenne_creneau * (position - 1)
        creneau = now + datetime.timedelta(minutes=minutes)

        # 9 Ticket
        ticket = Ticket.objects.create(
            client=client,
            file_attente=file_dattente,
            type_ticket=Ticket.TypeTicket.FILE_D_ATTENTE,
            position=position,
            creneau_prevue=creneau
        )

        # 10 Mise à jour file
        file_dattente.nombre_clients += 1
        file_dattente.save(update_fields=["nombre_clients"])

        return Response(
            {
                "message": "Client ajouté dans la file",
                "ticket": {
                    "ticket_id": ticket.ticket_id,
                    "code_ticket": ticket.code_ticket,
                    "position": ticket.position,
                    "creneau_prevue": ticket.creneau_prevue,
                    "etat_ticket": ticket.etat_ticket
                }
            },
            status=status.HTTP_201_CREATED
        )