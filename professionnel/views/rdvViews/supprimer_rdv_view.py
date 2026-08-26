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


class SupprimerRdvView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Supprimer un rendez-vous",
        description="""
Supprime un RDV et met à jour automatiquement la file d’attente.

✔ Supprime le ticket associé  
✔ Recalcule les positions  
✔ Maintient la cohérence du système  
""",

        parameters=[
            OpenApiParameter(
                name="rdv_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID du rendez-vous"
            )
        ],

        responses={
            200: OpenApiResponse(
                description="RDV supprimé avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={"message": "RDV supprimé avec succès"}
                    )
                ]
            ),

            404: OpenApiResponse(
                description="RDV introuvable",
                examples=[
                    OpenApiExample(
                        "Not found",
                        value={"error": "RDV introuvable"}
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur métier",
                examples=[
                    OpenApiExample(
                        "Erreur",
                        value={"error": "Ticket associé introuvable"}
                    )
                ]
            )
        }
    )
    def delete(self, request, rdv_id):
        utilisateur = request.user

        #  Récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  récupérer RDV
        try:
            rdv = RDV.objects.select_related(
                "service"
            ).get(
                rdv_id=rdv_id,
                service__professionnel=professionnel
            )
        except RDV.DoesNotExist:
            return Response(
                {"error": "RDV introuvable ou non autorisé"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            rdv.delete()

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "RDV supprimé avec succès"},
            status=status.HTTP_200_OK
        )