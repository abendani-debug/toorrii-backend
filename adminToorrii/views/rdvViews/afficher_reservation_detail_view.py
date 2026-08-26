from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample
)
from drf_spectacular.types import OpenApiTypes

from adminToorrii.models import RDV
from adminToorrii.serializers import AfficherReservationDetailRDVSerializer
from adminToorrii.permissions import IsAdminUserCustom


class AfficherDetailReservationView(APIView):
    """
    Endpoint : Détail complet d’un rendez-vous (RDV)
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["RDV"],
        summary="Afficher le détail d’un rendez-vous",
        description="""
Cet endpoint permet de récupérer les informations complètes d’un rendez-vous (RDV)
à partir de son identifiant `rdv_id`.

 Informations retournées :

 **Client**
- ID client
- Nom
- Prénom
- Numéro de téléphone
- Email

 **Service**
- ID service
- Nom du service
- Prix

 **Rendez-vous**
- Date et heure
- Statut (En_attente, Confirmer, Annuler, Terminer, Absent)
- Mode de réservation
- Durée
- Commentaire
- Date de création
- Statut email

 **Ticket associé**
- ID ticket
- Position dans la file
- Créneau prévu
- Type de ticket
- Code ticket
- Notification envoyée ou non
- Date de validation
- Date de création

 **Sécurité**
- Accessible uniquement par un administrateur
""",

        #  PATH PARAM CORRECT
        parameters=[
            OpenApiParameter(
                name="rdv_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant du rendez-vous (ex: RDV_12)"
            )
        ],

        #  RESPONSE SERIALIZER
        responses={
            200: OpenApiResponse(
                response=AfficherReservationDetailRDVSerializer,
                description="Détail du rendez-vous récupéré avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "rdv_id": "RDV_12",
                            "client": "CLN_1",
                            "client_nom": "Ahmed",
                            "client_prenom": "Benali",
                            "client_numero_telephone": "+213675902494",
                            "client_email": "ahmed@email.com",
                            "service": "SER_1",
                            "service_nom": "Consultation générale",
                            "service_prix": 2500,
                            "date_heure_rdv": "2026-03-10T10:30:00",
                            "statut_rdv": "Confirmer",
                            "rdv_date_demande": "2026-03-01T09:00:00",
                            "mail_envoye": True,
                            "duree": 30,
                            "mode_reservation": "En_ligne",
                            "commentaire_client": "Je préfère le matin",
                            "actif": True,
                            "ticket_id": "TKT_45",
                            "ticket_position": 5,
                            "ticket_creneau": "2026-03-10T10:30:00",
                            "ticket_type": "RDV",
                            "ticket_code": "ABC123",
                            "ticket_notification": True,
                            "ticket_date_validation": "2026-03-01T09:05:00",
                            "ticket_date_creation": "2026-03-01T09:00:00"
                        }
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Rendez-vous non trouvé",
                examples=[
                    OpenApiExample(
                        "RDV introuvable",
                        value={
                            "error": "RDV avec l'ID RDV_99 non trouvé"
                        }
                    )
                ]
            ),

            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Non autorisé",
                        value={
                            "detail": "Vous n'avez pas la permission d'effectuer cette action."
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, rdv_id):

        try:
            rdv = RDV.objects.get(rdv_id=rdv_id)
        except RDV.DoesNotExist:
            return Response(
                {"error": f"RDV avec l'ID {rdv_id} non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AfficherReservationDetailRDVSerializer(rdv)

        return Response(serializer.data, status=status.HTTP_200_OK)