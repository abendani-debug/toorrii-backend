from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
)

from adminToorrii.models import RDV
from client.serializers import DemandeProfileClientSerializer


class AnnulerRdvClientView(APIView):
    """
    Endpoint permettant à un client d’annuler un rendez-vous.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["RDV Client"],

        summary="Annuler un rendez-vous",

        description=(
            "Permet à un client d’annuler un rendez-vous existant.\n\n"

            " Fonctionnalités :\n"
            "- Changement du statut du rendez-vous vers 'Annuler'\n"
            "- Conservation de l’historique du rendez-vous\n"
            "- Empêche toute nouvelle modification après annulation\n\n"

            " Contraintes métier :\n"
            "- Le rendez-vous doit exister\n"
            "- Un rendez-vous déjà annulé ne peut pas être réannulé\n"
            "- Un rendez-vous terminé ne peut pas être annulé\n\n"

            " Endpoint public destiné au client."
        ),

        parameters=[
            OpenApiParameter(
                name="rdv_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant du rendez-vous (ex: RDV_1)"
            )
        ],

        responses={

            200: OpenApiResponse(
                description="Rendez-vous annulé avec succès",
                examples=[
                    OpenApiExample(
                        name="Annulation réussie",
                        value={
                            "message": "Rendez-vous annulé avec succès",
                            "rdv_id": "RDV_1",
                            "statut_rdv": "Annuler"
                        },
                        response_only=True,
                        status_codes=["200"]
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur métier",
                examples=[

                    OpenApiExample(
                        name="Déjà annulé",
                        value={
                            "error": "Ce rendez-vous est déjà annulé"
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="RDV terminé",
                        value={
                            "error": "Impossible d’annuler un rendez-vous terminé"
                        },
                        response_only=True,
                        status_codes=["400"]
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Rendez-vous introuvable",
                examples=[
                    OpenApiExample(
                        name="RDV introuvable",
                        value={
                            "error": "Rendez-vous introuvable"
                        },
                        response_only=True,
                        status_codes=["404"]
                    )
                ]
            )
        }
    )
    def patch(self, request, rdv_id):

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

        # Vérification existence RDV
        try:
            rdv = RDV.objects.get(pk=rdv_id)

        except RDV.DoesNotExist:
            return Response(
                {"error": "Rendez-vous introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérification statut actuel
        if rdv.statut_rdv == "Annuler":
            return Response(
                {"error": "Ce rendez-vous est déjà annulé"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if rdv.statut_rdv == "Terminer":
            return Response(
                {"error": "Impossible d’annuler un rendez-vous terminé"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mise à jour statut
        rdv.statut_rdv = "Annuler"
        rdv.save(update_fields=["statut_rdv"])

        return Response(
            {
                "message": "Rendez-vous annulé avec succès",
                "rdv_id": rdv.rdv_id,
                "statut_rdv": rdv.statut_rdv
            },
            status=status.HTTP_200_OK
        )