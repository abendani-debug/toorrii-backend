from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes
)

from adminToorrii.models import RDV, Professionnel, Service
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import RdvListSerializer


class ListRdvParServiceProView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],

        summary="Lister les rendez-vous d’un service",

        description=(
            "Cet endpoint permet au professionnel connecté de récupérer "
            "tous les rendez-vous associés à un service spécifique.\n\n"

            "Fonctionnalités :\n"
            "- Retourne uniquement les RDV du service demandé\n"
            "- Vérifie que le service appartient au professionnel connecté\n"
            "- Trie les RDV du plus récent au plus ancien\n"
            "- Inclut les informations du client, service et ticket\n\n"

            "Sécurité :\n"
            "- Authentification obligatoire\n"
            "- Accès réservé aux professionnels\n"
            "- Isolation stricte des données\n"
            "- Impossible d’accéder aux RDV d’un autre professionnel\n"
        ),

        parameters=[
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description=(
                    "Identifiant unique du service.\n\n"
                    "Exemple : `SER_1`"
                )
            )
        ],

        responses={

            200: OpenApiResponse(
                response=RdvListSerializer(many=True),
                description="Liste des rendez-vous récupérée avec succès",

                examples=[
                    OpenApiExample(
                        name="Succès",
                        summary="Exemple de réponse réussie",
                        description="Retourne la liste des RDV du service",
                        value={
                            "count": 2,

                            "service": {
                                "service_id": "SER_1",
                                "nom": "Consultation"
                            },

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
                                },

                                {
                                    "rdv_id": "RDV_2",
                                    "date_heure_rdv": "2026-05-10T14:00:00",
                                    "duree": 45,
                                    "statut_rdv": "En_attente",
                                    "mode_reservation": "Sur_place",

                                    "client": {
                                        "nom": "Sara",
                                        "prenom": "Khaled",
                                        "telephone": "+213555111222"
                                    },

                                    "service": {
                                        "service_id": "SER_1",
                                        "nom": "Consultation"
                                    },

                                    "ticket": {
                                        "ticket_id": 15,
                                        "position": 5,
                                        "type": "RDV"
                                    }
                                }
                            ]
                        }
                    )
                ]
            ),

            401: OpenApiResponse(
                description="Utilisateur non authentifié",

                examples=[
                    OpenApiExample(
                        name="Non authentifié",
                        value={
                            "detail": (
                                "Les informations "
                                "d'authentification n'ont pas été fournies."
                            )
                        }
                    )
                ]
            ),

            403: OpenApiResponse(
                description="Accès refusé",

                examples=[
                    OpenApiExample(
                        name="Permission refusée",
                        value={
                            "detail": (
                                "Vous n'avez pas la permission "
                                "d'effectuer cette action."
                            )
                        }
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Service ou profil professionnel introuvable",

                examples=[

                    OpenApiExample(
                        name="Profil professionnel introuvable",
                        value={
                            "error": "Profil professionnel introuvable."
                        }
                    ),

                    OpenApiExample(
                        name="Service introuvable",
                        value={
                            "error": (
                                "Service introuvable ou non autorisé."
                            )
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, service_id):

        utilisateur = request.user

        # récupérer professionnel connecté
        try:
            professionnel = utilisateur.professionnel_profile

        except Professionnel.DoesNotExist:
            return Response(
                {
                    "error": "Profil professionnel introuvable."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # vérifier que le service appartient au professionnel
        try:
            service = Service.objects.get(
                pk=service_id,
                professionnel=professionnel
            )

        except Service.DoesNotExist:
            return Response(
                {
                    "error": "Service introuvable ou non autorisé."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # récupérer uniquement les RDV du service
        rdvs = RDV.objects.select_related(
            "client",
            "service",
            "ticket"
        ).filter(
            service=service
        ).order_by("-date_heure_rdv")

        serializer = RdvListSerializer(
            rdvs,
            many=True
        )

        return Response(
            {
                "count": rdvs.count(),

                "service": {
                    "service_id": service.service_id,
                    "nom": service.nom_service
                },

                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )