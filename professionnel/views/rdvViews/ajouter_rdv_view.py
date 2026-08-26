from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)

from professionnel.serializers import RdvSerializer
from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import Service, Professionnel


class AjouterRdvView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Créer un rendez-vous (Professionnel)",
        description=(
            "Permet à un professionnel de créer un rendez-vous pour un service donné.\n\n"
            " Fonctionnalités :\n"
            "- Création automatique du client si inexistant\n"
            "- Vérification du planning (jour, horaires, pauses)\n"
            "- Vérification des exceptions\n"
            "- Vérification disponibilité du créneau\n"
            "- Génération automatique d’un ticket (file d’attente)\n\n"
            " Sécurité :\n"
            "- Le service doit appartenir au professionnel connecté\n"
        ),

        #  PATH PARAM
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du service (ex: SER_1)"
            )
        ],

        #  REQUEST BODY
        request=RdvSerializer,

        #  RESPONSES
        responses={
            201: OpenApiResponse(
                description="Rendez-vous créé avec succès",
                response=RdvSerializer,
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "date_heure_rdv": "2026-05-11T10:30:00",
                            "duree": 30,
                            "client": {
                                "nom": "Ali",
                                "prenom": "Ahmed",
                                "numero_telephone": "+213675902494",
                                "email": "ali@email.com"
                            },
                            "service": {
                                "id": "SER_1",
                                "nom": "Consultation"
                            },
                            "ticket": {
                                "id": 12,
                                "position": 3,
                                "type_ticket": "RDV",
                                "creneau_prevue": "2026-05-11T10:30:00"
                            }
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation métier",
                examples=[
                    OpenApiExample(
                        "Créneau occupé",
                        value={"error": "Ce créneau est déjà réservé"}
                    ),
                    OpenApiExample(
                        "Hors horaires",
                        value={"error": "Créneau hors horaires du service"}
                    ),
                    OpenApiExample(
                        "Pause",
                        value={"error": "Créneau dans une pause du service"}
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
                description="Ressource introuvable",
                examples=[
                    OpenApiExample(
                        "Service introuvable",
                        value={"error": "Service introuvable ou non autorisé"}
                    ),
                    OpenApiExample(
                        "Profil professionnel introuvable",
                        value={"error": "Profil professionnel introuvable."}
                    )
                ]
            )
        }

        
    )
    def post(self, request, service_id):

        utilisateur = request.user

        #  Récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  Vérifier service appartient au professionnel
        try:
            service = Service.objects.get(
                pk=service_id,
                professionnel=professionnel
            )
        except Service.DoesNotExist:
            return Response(
                {"error": "Service introuvable ou non autorisé"},
                status=status.HTTP_404_NOT_FOUND
            )

        #  Injection service_id dans les données
        data = request.data.copy()
        data["service_id"] = service_id

        serializer = RdvSerializer(data=data)

        if serializer.is_valid():
            rdv = serializer.save()

            return Response(
                RdvSerializer(rdv).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )