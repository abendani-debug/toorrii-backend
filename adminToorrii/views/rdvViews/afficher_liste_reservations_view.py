from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

from adminToorrii.models import RDV
from adminToorrii.serializers import AfficherListReservationSerializer
from adminToorrii.permissions import IsAdminUserCustom


class AfficherListeReservationsClientsView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["RDV"],
        summary="Lister les réservations actives des clients",
        description=(
            "Retourne la liste des rendez-vous actifs des clients "
            "(statuts : **En_attente** ou **Confirmer**).\n\n"

            " Données retournées :\n"
            "- Informations client\n"
            "- Nom du service\n"
            "- Date et heure du RDV\n"
            "- Statut et mode de réservation\n"
            "- Commentaire client\n"
            "- Ticket associé (id, position, type, créneau, code)\n\n"

            " Filtres optionnels :\n"
            "- `client_id` : filtrer par client\n"
            "- `service_id` : filtrer par service\n"
            "- `date` : filtrer par date (format YYYY-MM-DD)\n\n"

            " Accès réservé aux administrateurs"
        ),

        #  QUERY PARAMS CORRECTS
        parameters=[
            OpenApiParameter(
                name="client_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtrer par ID client (ex: CLN_1)"
            ),
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtrer par ID service (ex: SER_1)"
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filtrer par date du RDV (format YYYY-MM-DD)"
            ),
        ],

        #  RESPONSE PROPRE
        responses={
            200: OpenApiResponse(
                description="Liste des réservations récupérée avec succès",
                response=AfficherListReservationSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "rdvs": [
                                {
                                    "rdv_id": "RDV_12",
                                    "client": "CLN_1 - Ahmed Benali",
                                    "client_nom": "ziad",
                                    "client_prenom": "ziad",
                                    "client_numero_telephone": "+213675902494",
                                    "client_email": "ziad@gmail.com",
                                    "service": "SER_2",
                                    "service_nom": "Consultation générale",
                                    "date_heure_rdv": "2026-03-10T10:30:00",
                                    "statut_rdv": "Confirmer",
                                    "duree": 30,
                                    "mode_reservation": "En_ligne",
                                    "actif": True,
                                    "commentaire_client": "Je préfère le matin",
                                    "ticket_id": "TKT_45",
                                    "ticket_position": 5,
                                    "ticket_creneau": "2026-03-10T10:30:00",
                                    "ticket_type": "RDV",
                                    "ticket_code": "ABC123"
                                }
                            ]
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation (ex: format date invalide)",
                examples=[
                    OpenApiExample(
                        "Date invalide",
                        value={"error": "Format de date invalide (YYYY-MM-DD)"}
                    )
                ]
            ),

            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Non autorisé",
                        value={"detail": "Vous n'avez pas la permission d'effectuer cette action."}
                    )
                ]
            )
        },

        #  EXEMPLES D’URL
        examples=[
            OpenApiExample(
                "Sans filtre",
                summary="Récupérer tous les RDV actifs",
                value="/api/rdv/list/",
                request_only=True
            ),
            OpenApiExample(
                "Filtre par client",
                value="/api/rdv/list/?client_id=CLN_1",
                request_only=True
            ),
            OpenApiExample(
                "Filtre par date",
                value="/api/rdv/list/?date=2026-03-10",
                request_only=True
            )
        ]
    )

    def get(self, request):
        client_id = request.query_params.get("client_id")
        service_id = request.query_params.get("service_id")
        date_param = request.query_params.get("date")

        rdvs = RDV.objects.filter(
            statut_rdv__in=["En_attente", "Confirmer"]
        )

        if client_id:
            rdvs = rdvs.filter(client__id_client=client_id)

        if service_id:
            rdvs = rdvs.filter(service__service_id=service_id)

        if date_param:
            rdvs = rdvs.filter(date_heure_rdv__date=date_param)

        serializer = AfficherListReservationSerializer(rdvs, many=True)

        return Response(
            {"rdvs": serializer.data},
            status=status.HTTP_200_OK
        )