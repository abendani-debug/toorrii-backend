from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from adminToorrii.models import Ticket
from client.serializers import (
    RdvSerializer,
    DemandeProfileClientSerializer
)


class ModifierRdvClientView(APIView):
    """
    Endpoint permettant à un client
    de modifier son rendez-vous.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["RDV Client"],

        summary="Modifier un rendez-vous client",

        description=(
            "Permet à un client de modifier un rendez-vous "
            "à l’aide :\n\n"

            "- Du numéro de téléphone du client\n"
            "- Du code ticket du rendez-vous\n\n"

            " Vérifications effectuées :\n"
            "- Validation format du numéro téléphone\n"
            "- Validation format du code ticket\n"
            "- Vérification existence du ticket\n"
            "- Vérification existence du rendez-vous\n"
            "- Vérification appartenance du rendez-vous au client\n"
            "- Vérification disponibilité du créneau\n"
            "- Vérification conflits et chevauchements\n"
            "- Vérification horaires du service\n"
            "- Vérification pauses et exceptions\n\n"

            " Contraintes métier :\n"
            "- Les rendez-vous annulés ne peuvent pas être modifiés\n"
            "- Les rendez-vous terminés ne peuvent pas être modifiés\n"
            "- Aucun chevauchement n’est autorisé\n"
            "- Le créneau doit être valide\n\n"

            " Actions effectuées :\n"
            "- Mise à jour du rendez-vous\n"
            "- Mise à jour automatique du ticket associé"
        ),

        request=RdvSerializer,

        responses={

            200: OpenApiResponse(
                description="Rendez-vous modifié avec succès",
                response=RdvSerializer,
                examples=[
                    OpenApiExample(
                        name="Modification réussie",
                        value={
                            "message": (
                                "Rendez-vous modifié avec succès"
                            ),

                            "rdv": {
                                "date_heure_rdv": (
                                    "2026-05-20T15:00:00"
                                ),

                                "client": {
                                    "nom": "Ali",
                                    "prenom": "Ahmed",
                                    "numero_telephone": (
                                        "+213675902494"
                                    ),
                                    "email": "ali@email.com"
                                },

                                "service": {
                                    "service_id": "SER_1",
                                    "nom_service": (
                                        "Consultation"
                                    )
                                },

                                "ticket": {
                                    "ticket_id": "TCK_12",
                                    "position": 5,
                                    "type_ticket": "RDV",
                                    "creneau_prevue": (
                                        "2026-05-20T15:00:00"
                                    )
                                }
                            }
                        },
                        response_only=True,
                        status_codes=["200"]
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur validation métier",
                examples=[

                    OpenApiExample(
                        name="Code ticket invalide",
                        value={
                            "code_ticket": [
                                (
                                    "Format invalide. "
                                    "Exemple : "
                                    "CTK-20260427-0001"
                                )
                            ]
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Numéro téléphone invalide",
                        value={
                            "numero_telephone": [
                                (
                                    "Le numéro de téléphone "
                                    "doit être au format "
                                    "algérien (+213)"
                                )
                            ]
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Téléphone incorrect",
                        value={
                            "error": (
                                "Le numéro de téléphone "
                                "ne correspond pas "
                                "au rendez-vous"
                            )
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Créneau occupé",
                        value={
                            "error": (
                                "Ce créneau est déjà réservé"
                            )
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Chevauchement",
                        value={
                            "error": (
                                "Le créneau chevauche "
                                "un autre rendez-vous"
                            )
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="RDV annulé",
                        value={
                            "error": (
                                "Impossible de modifier "
                                "un rendez-vous annulé"
                            )
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="RDV terminé",
                        value={
                            "error": (
                                "Impossible de modifier "
                                "un rendez-vous terminé"
                            )
                        },
                        response_only=True,
                        status_codes=["400"]
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Ressource introuvable",
                examples=[

                    OpenApiExample(
                        name="Ticket introuvable",
                        value={
                            "error": "Ticket introuvable"
                        },
                        response_only=True,
                        status_codes=["404"]
                    ),

                    OpenApiExample(
                        name="RDV introuvable",
                        value={
                            "error": (
                                "Rendez-vous introuvable"
                            )
                        },
                        response_only=True,
                        status_codes=["404"]
                    )
                ]
            )
        },

        examples=[

            OpenApiExample(
                name="Exemple requête modification",
                request_only=True,
                value={

                    "numero_telephone": (
                        "+213675902494"
                    ),

                    "code_ticket": (
                        "CTK-20260427-0001"
                    ),

                    "date_heure_rdv": (
                        "2026-05-20T15:00:00"
                    ),

                    "client_nom": "Ali",

                    "client_prenom": "Ahmed",

                    "client_email": (
                        "ali@email.com"
                    ),

                    "commentaire_client": (
                        "Je serai en retard de 5 minutes"
                    )
                }
            )
        ]
    )
    def patch(self, request):

        # =====================================================
        # RÉCUPÉRATION DONNÉES AUTHENTIFICATION CLIENT
        # =====================================================

        numero_telephone = request.data.get(
            "numero_telephone"
        )

        code_ticket = request.data.get(
            "code_ticket"
        )

        # =====================================================
        # VALIDATION NUMÉRO + CODE TICKET
        # =====================================================

        demande_serializer = (
            DemandeProfileClientSerializer(
                data={
                    "numero_telephone": (
                        numero_telephone
                    ),
                    "code_ticket": code_ticket
                }
            )
        )

        if not demande_serializer.is_valid():

            return Response(
                demande_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_demande_data = (
            demande_serializer.validated_data
        )

        numero_telephone = (
            validated_demande_data[
                "numero_telephone"
            ]
        )

        code_ticket = (
            validated_demande_data[
                "code_ticket"
            ]
        )

        # =====================================================
        # RECHERCHE TICKET
        # =====================================================

        try:

            ticket = Ticket.objects.select_related(
                "rdv",
                "rdv__client",
                "rdv__service"
            ).get(
                code_ticket=code_ticket
            )

        except Ticket.DoesNotExist:

            return Response(
                {
                    "error": "Ticket introuvable"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # =====================================================
        # RECHERCHE RDV
        # =====================================================

        rdv = ticket.rdv

        if not rdv:

            return Response(
                {
                    "error": (
                        "Rendez-vous introuvable"
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # =====================================================
        # VÉRIFICATION PROPRIÉTAIRE RDV
        # =====================================================

        if (
            str(rdv.client.numero_telephone)
            != str(numero_telephone)
        ):

            return Response(
                {
                    "error": (
                        "Le numéro de téléphone "
                        "ne correspond pas "
                        "au rendez-vous"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =====================================================
        # VÉRIFICATION STATUT RDV
        # =====================================================

        if rdv.statut_rdv == "Annuler":

            return Response(
                {
                    "error": (
                        "Impossible de modifier "
                        "un rendez-vous annulé"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if rdv.statut_rdv == "Terminer":

            return Response(
                {
                    "error": (
                        "Impossible de modifier "
                        "un rendez-vous terminé"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =====================================================
        # PRÉPARATION DONNÉES UPDATE
        # =====================================================

        update_data = request.data.copy()

        # Injection service_id automatiquement
        update_data["service_id"] = (
            rdv.service.service_id
        )

        # Mapping vers champ serializer RDV
        update_data[
            "client_numero_telephone"
        ] = numero_telephone

        # Nettoyage champs inutiles
        update_data.pop("numero_telephone", None)
        update_data.pop("code_ticket", None)

        # =====================================================
        # VALIDATION + UPDATE RDV
        # =====================================================

        serializer = RdvSerializer(
            rdv,
            data=update_data,
            partial=True
        )

        if serializer.is_valid():

            rdv = serializer.save()

            return Response(
                {
                    "message": (
                        "Rendez-vous modifié "
                        "avec succès"
                    ),

                    "rdv": (
                        RdvSerializer(rdv).data
                    )
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )