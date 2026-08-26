from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

from adminToorrii.serializers import CreateRDVSerializer
from adminToorrii.models import Service
from adminToorrii.permissions import IsAdminUserCustom


class AjouterRdvView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["RDV"],
        summary="Créer un rendez-vous avec ticket automatique",
        description=(
            "Cet endpoint permet de créer un rendez-vous pour un client.\n\n"

            " Règles métier appliquées automatiquement :\n"
            "- Vérification que le service existe\n"
            "- Vérification du planning (jour de travail)\n"
            "- Vérification des horaires du service\n"
            "- Vérification des pauses\n"
            "- Vérification des exceptions\n"
            "- Vérification que le créneau n’est pas déjà réservé\n\n"

            " Automatisations :\n"
            "- Création automatique du client si inexistant (via téléphone)\n"
            "- Création automatique de la file d’attente du jour\n"
            "- Génération automatique d’un ticket\n"
            "- Calcul automatique de la position dans la file\n\n"

            " Sécurité :\n"
            "- Endpoint accessible uniquement aux administrateurs"
        ),

        #  PATH PARAM
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant du service (ex: SER_1)"
            )
        ],

        #  REQUEST BODY
        request=CreateRDVSerializer,

        #  RESPONSES
        responses={
            201: OpenApiResponse(
                description="Rendez-vous créé avec succès",
                response=CreateRDVSerializer,
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "date_heure_rdv": "2026-05-11T10:30:00",
                            "commentaire_client": "",
                            "client": {
                                "client_nom": "Ali",
                                "client_prenom": "Ahmed",
                                "client_numero_telephone": "+213675902494",
                                "client_email": "ali@email.com"
                            },
                            "service": {
                                "service_id": "SER_1",
                                "nom_service": "Consultation"
                            },
                            "ticket": {
                                "id": "TKT_12",
                                "position": 3,
                                "type_ticket": "RDV",
                                "creneau_prevue": "2026-05-11T10:30:00"
                            }
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation ou règle métier",
                examples=[
                    OpenApiExample(
                        "Créneau déjà réservé",
                        value={"error": "Ce créneau est déjà réservé"}
                    ),
                    OpenApiExample(
                        "Hors horaires",
                        value={"error": "Créneau hors horaires du service"}
                    ),
                    OpenApiExample(
                        "Pause",
                        value={"error": "Créneau dans une pause du service"}
                    ),
                    OpenApiExample(
                        "Exception planning",
                        value={"error": "Service indisponible (exception planning)"}
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Service introuvable",
                examples=[
                    OpenApiExample(
                        "Service non trouvé",
                        value={"error": "Service introuvable ou non autorisé"}
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
            )
        },

        #  EXEMPLES DE REQUÊTES
        examples=[
            OpenApiExample(
                "Création minimale",
                summary="Créer un RDV avec téléphone uniquement",
                value={
                    "date_heure_rdv": "2026-05-11T10:30:00",
                    "client_numero_telephone": "0675902494"
                },
                request_only=True
            ),
            OpenApiExample(
                "Création complète",
                summary="Créer un RDV avec toutes les informations",
                value={
                    "date_heure_rdv": "2026-05-11T10:30:00",
                    "client_numero_telephone": "0675902494",
                    "client_nom": "Ali",
                    "client_prenom": "Ahmed",
                    "client_email": "ali@email.com",
                    "commentaire_client": "Je préfère le matin"
                },
                request_only=True
            )
        ]
    )

    def post(self, request, service_id):

        #  Vérifier service
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            return Response(
                {"error": "Service introuvable ou non autorisé"},
                status=status.HTTP_404_NOT_FOUND
            )

        #  Injecter service_id
        data = request.data.copy()
        data["service_id"] = service_id

        #  Validation serializer
        serializer = CreateRDVSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Création RDV
        rdv = serializer.save()

        #  Réponse
        return Response(
            CreateRDVSerializer(rdv).data,
            status=status.HTTP_201_CREATED
        )