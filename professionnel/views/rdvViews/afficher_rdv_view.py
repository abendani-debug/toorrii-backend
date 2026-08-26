from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample
)

from adminToorrii.models import RDV, Professionnel
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import RdvListSerializer


class ListRdvProView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Lister tous les rendez-vous du professionnel connecté",
        description=(
            "Cet endpoint permet au professionnel connecté de récupérer "
            "la liste de tous ses rendez-vous.\n\n"

            " Fonctionnalités :\n"
            "- Récupère uniquement les RDV du professionnel connecté\n"
            "- Triés du plus récent au plus ancien\n"
            "- Inclut les informations client, service et ticket associé\n\n"

            " Sécurité :\n"
            "- Accès uniquement au professionnel authentifié\n"
            "- Isolation des données par professionnel\n"
        ),

        responses={
            200: OpenApiResponse(
                description="Liste des rendez-vous récupérée avec succès",
                response=RdvListSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "count": 2,
                            "results": [
                                {
                                    "rdv_id": "RDV_1",
                                    "date_heure_rdv": "2026-05-11T10:30:00",
                                    "duree": 30,
                                    "statut_rdv": "Confirmer",
                                    "mode_reservation": "En_ligne",
                                    "client": {
                                        "nom": "Ali",
                                        "prenom": "Ahmed",
                                        "telephone": "+213675902494"
                                    },
                                    "service": {
                                        "service_id": "SER_1",
                                        "nom": "Consultation"
                                    },
                                    "ticket": {
                                        "ticket_id": 12,
                                        "position": 3,
                                        "type": "RDV"
                                    }
                                }
                            ]
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
            ),

            404: OpenApiResponse(
                description="Profil professionnel introuvable",
                examples=[
                    OpenApiExample(
                        "Profil manquant",
                        value={
                            "error": "Profil professionnel introuvable."
                        }
                    )
                ]
            )
        }
    )
    def get(self, request):

        utilisateur = request.user

        #  récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  récupérer RDV
        rdvs = RDV.objects.select_related(
            "client",
            "service"
        ).filter(
            service__professionnel=professionnel
        ).order_by("-date_heure_rdv")

        serializer = RdvListSerializer(rdvs, many=True)

        return Response(
            {
                "count": rdvs.count(),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )