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
from professionnel.serializers import RdvDetailSerializer


class AfficherDetailRdvView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Détails d’un rendez-vous",
        description=(
            "Permet au professionnel de consulter les détails d’un RDV.\n\n"
            " Retourne :\n"
            "- Informations du RDV\n"
            "- Informations du client\n"
            "- Informations du service\n"
            "- Ticket associé\n\n"
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
                description="Détails du RDV",
                response=RdvDetailSerializer,
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "rdv_id": "RDV_1",
                            "date_heure_rdv": "2026-05-11T10:30:00",
                            "duree": 30,
                            "statut_rdv": "Confirmer",
                            "mode_reservation": "En_ligne",
                            "commentaire_client": "Je préfère le matin",
                            "date_demande": "2026-05-10T12:00:00",
                            "client": {
                                "nom": "Ali",
                                "prenom": "Ahmed",
                                "numero_telephone": "+213675902494",
                                "email": "ali@email.com"
                            },
                            "service": {
                                "service_id": "SER_1",
                                "nom": "Consultation"
                            },
                            "ticket": {
                                "ticket_id": 5,
                                "position": 2,
                                "type_ticket": "RDV",
                                "creneau_prevue": "2026-05-11T10:30:00"
                            }
                        }
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
    def get(self, request, rdv_id):

        utilisateur = request.user

        #  récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  récupérer RDV sécurisé + optimisation
        try:
            rdv = RDV.objects.select_related(
                "client",
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

        serializer = RdvDetailSerializer(rdv)

        return Response(serializer.data, status=status.HTTP_200_OK)