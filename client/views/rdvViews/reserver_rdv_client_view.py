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

from client.serializers import RdvSerializer
from adminToorrii.models import Service
from client.utils.brevo_service import send_client_rdv_notification

class ReserverRdvClientView(APIView):
    """
    Endpoint dédié au client pour réserver un rendez-vous.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["RDV Client"],

        summary="Réserver un rendez-vous",

        description=(
            "Permet à un client de réserver un rendez-vous pour un service donné.\n\n"

            " Fonctionnalités principales :\n"
            "- Création automatique du client si inexistant\n"
            "- Vérification du planning du service\n"
            "- Vérification des horaires d’ouverture\n"
            "- Vérification des pauses du professionnel\n"
            "- Vérification des exceptions et indisponibilités\n"
            "- Vérification des conflits et chevauchements de créneaux\n"
            "- Génération automatique d’un ticket de passage\n\n"

            " Logique métier :\n"
            "- Le rendez-vous doit respecter la durée du service\n"
            "- Aucun chevauchement avant ou après n’est autorisé\n"
            "- Le créneau doit être disponible\n"
            "- Le ticket est généré automatiquement après validation\n\n"

            " Remarques :\n"
            "- Endpoint public destiné aux clients\n"
            "- Aucune authentification requise\n"
            "- Le service doit exister dans la plateforme"
        ),

        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant unique du service (ex: SER_1)"
            )
        ],

        request=RdvSerializer,

        responses={

            201: OpenApiResponse(
                description="Rendez-vous réservé avec succès",
                response=RdvSerializer,
                examples=[
                    OpenApiExample(
                        name="Réservation réussie",
                        value={
                            "id": "RDV_15",
                            "date_heure_rdv": "2026-05-15T10:30:00",
                            "duree": 30,
                            "statut_rdv": "En_attente",

                            "client": {
                                "id": "CLI_10",
                                "nom": "Ali",
                                "prenom": "Ahmed",
                                "numero_telephone": "+213675902494",
                                "email": "ali@email.com"
                            },

                            "service": {
                                "id": "SER_1",
                                "nom": "Consultation Médicale"
                            },

                            "ticket": {
                                "id": 12,
                                "position": 3,
                                "type_ticket": "RDV",
                                "creneau_prevue": "2026-05-15T10:30:00"
                            }
                        },
                        response_only=True,
                        status_codes=["201"]
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation métier",
                examples=[

                    OpenApiExample(
                        name="Créneau déjà réservé",
                        value={
                            "error": "Ce créneau est déjà réservé"
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Chevauchement détecté",
                        value={
                            "error": "Le créneau chevauche un autre rendez-vous"
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Hors horaires",
                        value={
                            "error": "Créneau hors horaires du service"
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Pause du professionnel",
                        value={
                            "error": "Créneau dans une pause du service"
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Exception planning",
                        value={
                            "error": "Le professionnel est indisponible sur ce créneau"
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Données invalides",
                        value={
                            "date_heure_rdv": [
                                "Ce champ est obligatoire."
                            ]
                        },
                        response_only=True,
                        status_codes=["400"]
                    ),
                ]
            ),

            404: OpenApiResponse(
                description="Service introuvable",
                examples=[
                    OpenApiExample(
                        name="Service inexistant",
                        value={
                            "error": "Service introuvable"
                        },
                        response_only=True,
                        status_codes=["404"]
                    )
                ]
            )
        },

        examples=[
            OpenApiExample(
                name="Exemple requête réservation",
                request_only=True,
                value={
                    "date_heure_rdv": "2026-05-15T10:30:00",
                    "duree": 30,

                    "client": {
                        "nom": "Ali",
                        "prenom": "Ahmed",
                        "numero_telephone": "+213675902494",
                        "email": "ali@email.com"
                    }
                }
            )
        ]
    )
    def post(self, request, service_id):

        # Vérification existence service
        try:
            service = Service.objects.get(pk=service_id)

        except Service.DoesNotExist:
            return Response(
                {"error": "Service introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Injection service_id
        data = request.data.copy()
        data["service_id"] = service_id

        serializer = RdvSerializer(data=data)

        if serializer.is_valid():

            # ── Vérification conflit de créneau ──────────────────────────────
            from adminToorrii.models import RDV
            from datetime import timedelta

            date_heure_rdv = serializer.validated_data.get("date_heure_rdv")
            duree_minutes = service.duree_moyenne_creneau

            STATUTS_ACTIFS = ["En_attente", "Confirmer"]

            if date_heure_rdv:
                date_heure_fin = date_heure_rdv + timedelta(minutes=duree_minutes)

                conflit = RDV.objects.filter(
                    service=service,
                    statut_rdv__in=STATUTS_ACTIFS,
                    date_heure_rdv__lt=date_heure_fin,
                    date_heure_rdv__gte=date_heure_rdv - timedelta(minutes=duree_minutes - 1),
                ).exists()

                if conflit:
                    return Response(
                        {"error": "Ce créneau est déjà réservé. Veuillez choisir un autre horaire."},
                        status=status.HTTP_409_CONFLICT
                    )
            # ─────────────────────────────────────────────────────────────────

            rdv = serializer.save()
            client = rdv.client

            send_client_rdv_notification(
                email=client.email,
                nom=client.nom,
                date_rdv=rdv.date_heure_rdv,
                service=rdv.service.nom_service if rdv.service else None
            )

            return Response(
                RdvSerializer(rdv).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )