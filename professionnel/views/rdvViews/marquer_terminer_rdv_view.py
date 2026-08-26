from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)

from adminToorrii.models import RDV, Professionnel
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.utils.rdv_service import RDVCreationService


class MarquerTerminerRdvProView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Marquer un RDV comme terminé (présent)",
        description=(
            "Permet à un professionnel de marquer un rendez-vous comme terminé.\n\n"
            " Fonctionnalités :\n"
            "- Vérifie que le RDV appartient au professionnel\n"
            "- Met à jour le statut → Terminer\n"
            "- Empêche les transitions invalides\n\n"
            " Sécurité :\n"
            "- Le RDV doit appartenir à un service du professionnel connecté\n"
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
                description="RDV marqué comme terminé",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "message": "RDV terminé avec succès",
                            "statut": "Terminer"
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur métier",
                examples=[
                    OpenApiExample(
                        "Déjà terminé",
                        value={"error": "RDV déjà terminé"}
                    ),
                    OpenApiExample(
                        "Annulé",
                        value={"error": "RDV annulé"}
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
            ),

            404: OpenApiResponse(
                description="RDV introuvable ou non autorisé",
                examples=[
                    OpenApiExample(
                        "RDV non trouvé",
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

        #  récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  récupérer RDV avec sécurité
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
            rdv.statut_rdv = "Terminer"
            rdv.save()

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "RDV terminé avec succès",
                "statut": rdv.statut_rdv
            },
            status=status.HTTP_200_OK
        )