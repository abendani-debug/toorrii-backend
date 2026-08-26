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
from professionnel.utils.brevo_service import send_rdv_cancellation_notification

class AnnulerRdvView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Refuser / Annuler un rendez-vous",
        description=(
            "Permet au professionnel d’annuler ou refuser un RDV.\n\n"
            " Fonctionnement :\n"
            "- Si confirmation automatique → annulation directe\n"
            "- Si confirmation manuelle :\n"
            "   • En_attente → Refus\n"
            "   • Confirmer → Annulation\n\n"
            " Résultat : statut = Annuler\n\n"
            " Sécurité :\n"
            "- Le RDV doit appartenir au professionnel connecté"
        ),

        parameters=[
            OpenApiParameter(
                name="rdv_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du RDV (ex: RDV_1)"
            )
        ],

        responses={

            200: OpenApiResponse(
                description="RDV annulé avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "message": "RDV annulé avec succès",
                            "statut": "Annuler"
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur métier",
                examples=[
                    OpenApiExample(
                        "Déjà annulé",
                        value={"error": "RDV déjà annulé"}
                    ),
                    OpenApiExample(
                        "Statut interdit",
                        value={"error": "Impossible d'annuler ce RDV"}
                    )
                ]
            ),

            403: OpenApiResponse(
                description="Accès refusé"
            ),

            404: OpenApiResponse(
                description="RDV introuvable ou non autorisé",
                examples=[
                    OpenApiExample(
                        "Not found",
                        value={"error": "RDV introuvable ou non autorisé"}
                    )
                ]
            )
        }
    )
    def patch(self, request, rdv_id):

        utilisateur = request.user

        #  récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  récupérer RDV sécurisé
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

        #  logique métier
        try:
            rdv.statut_rdv = "Annuler"
            rdv.save()


        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        # =====================================================
        # NOTIFICATION EMAIL CLIENT
        # =====================================================
        client = rdv.client

        if client and client.email:

            send_rdv_cancellation_notification(
                email=client.email,
                nom=client.nom,
                date_rdv=rdv.date_heure_rdv,
                service=rdv.service.nom_service if rdv.service else None
            )

        return Response(
            {
                "message": "RDV annulé avec succès",
                "statut": rdv.statut_rdv
            },
            status=status.HTTP_200_OK
        )