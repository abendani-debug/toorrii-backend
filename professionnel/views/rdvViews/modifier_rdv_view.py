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
from professionnel.serializers import RdvSerializer
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.utils.rdv_service import RDVCreationService


class ModifierRdvView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Modifier un rendez-vous",
        description="""
Permet de modifier un RDV existant.

✔ Vérifie les contraintes métier  
✔ Vérifie disponibilité du nouveau créneau  
✔ Met à jour le ticket automatiquement  
✔ Recalcule la position si nécessaire  
""",

        parameters=[
            OpenApiParameter(
                name="rdv_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID du rendez-vous"
            )
        ],

        request=RdvSerializer,

        responses={
            200: OpenApiResponse(
                description="RDV modifié avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "message": "RDV modifié avec succès",
                            "date_heure_rdv": "2026-05-11T11:00:00",
                            "ticket": {
                                "position": 4
                            }
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation",
                examples=[
                    OpenApiExample(
                        "Créneau occupé",
                        value={"error": "Ce créneau est déjà réservé"}
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
            )
        }
    )
    def put(self, request, rdv_id):

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

        #  Récupérer RDV
        rdv = get_object_or_404(RDV, rdv_id=rdv_id)

        #  Injecter data
        data = request.data.copy()

        #  Serializer validation
        serializer = RdvSerializer(rdv, data=data, partial=True)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            #  Logique métier
            rdv, ticket = RDVCreationService.update_rdv(rdv, serializer.validated_data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "RDV modifié avec succès",
                "data": RdvSerializer(rdv).data
            },
            status=status.HTTP_200_OK
        )