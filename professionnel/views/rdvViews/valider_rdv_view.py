from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)

from adminToorrii.models import RDV, Professionnel
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.utils.rdv_service import RDVCreationService
from professionnel.utils.brevo_service import send_rdv_validation_notification


class ValiderRdvView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Valider un rendez-vous (manuel)",
        description=(
            "Permet à un professionnel de valider un rendez-vous.\n\n"
            " Fonctionnement :\n"
            "- Si confirmation_rdv_auto = True → validation automatique (endpoint interdit)\n"
            "- Si confirmation_rdv_auto = False → validation manuelle requise\n\n"
            " Règles métier :\n"
            "- Le RDV doit être en statut 'En_attente'\n"
            "- Il devient 'Confirmer'\n\n"
            " Sécurité :\n"
            "- Le RDV doit appartenir au professionnel connecté\n"
        ),

        parameters=[
            OpenApiParameter(
                name="rdv_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du rendez-vous (ex: RDV_1)"
            )
        ],

        responses={

            200: OpenApiResponse(
                description="RDV validé avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "message": "RDV validé avec succès",
                            "statut": "Confirmer"
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur métier",
                examples=[
                    OpenApiExample(
                        "Auto",
                        value={
                            "error": "La confirmation des RDV est automatique pour ce professionnel"
                        }
                    ),
                    OpenApiExample(
                        "Déjà confirmé",
                        value={"error": "RDV déjà confirmé"}
                    ),
                    OpenApiExample(
                        "Statut invalide",
                        value={"error": "Impossible de valider ce RDV"}
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
            ),

            404: OpenApiResponse(
                description="RDV introuvable ou non autorisé",
                examples=[
                    OpenApiExample(
                        "RDV introuvable",
                        value={"error": "RDV introuvable ou non autorisé"}
                    ),
                    OpenApiExample(
                        "Profil professionnel introuvable",
                        value={"error": "Profil professionnel introuvable."}
                    )
                ]
            )
        }
    )
    def patch(self, request, rdv_id):

        utilisateur = request.user

        #  Récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        

        #  Récupérer RDV sécurisé
        try:
            rdv = RDV.objects.select_related("service").get(
                rdv_id=rdv_id,
                service__professionnel=professionnel
            )
        except RDV.DoesNotExist:
            return Response(
                {"error": "RDV introuvable ou non autorisé"},
                status=status.HTTP_404_NOT_FOUND
            )
            #  Vérifier configuration AUTO
        if professionnel.confirmation_rdv_auto:
            return Response(
                {"error": "La confirmation des RDV est automatique pour ce professionnel"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Logique métier
        try:
            rdv = RDVCreationService.valider_rdv(rdv)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        # =====================================================
            # NOTIFICATION CLIENT (BREVO)
        # =====================================================

        client = rdv.client

        if client and client.email:

            send_rdv_validation_notification(
                email=client.email,
                nom=client.nom,
                date_rdv=rdv.date_heure_rdv,
                service=rdv.service.nom_service if rdv.service else None
            )

        return Response(
            {
                "message": "RDV validé avec succès",
                "statut": rdv.statut_rdv
            },
            status=status.HTTP_200_OK
        )