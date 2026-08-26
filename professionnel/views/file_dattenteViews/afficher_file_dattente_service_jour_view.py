from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)
from drf_spectacular.types import OpenApiTypes

from adminToorrii.models import FileDattente, Service, Professionnel
from professionnel.serializers import FileDattenteSerializer
from adminToorrii.permissions import IsProfessionnelUserCustom


class AfficherFileDattenteView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["File d'attente Professionnel"],
        summary="Afficher la file d'attente d’un service (Professionnel)",
        description="""
Permet à un professionnel de consulter la file d’attente d’un de ses services
pour une date précise.

 Sécurité :
- Le service doit appartenir au professionnel connecté

 Paramètres :
- service_id (path)
- date (query param : YYYY-MM-DD)

 Données retournées :
- ID file
- Service
- Date
- Etat de la file
- Nombre de clients
- Temps moyen d’attente
""",

        parameters=[
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du service (ex: SER_1)"
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Date de la file (YYYY-MM-DD)"
            )
        ],

        responses={
            200: OpenApiResponse(
                response=FileDattenteSerializer,
                description="File d’attente récupérée avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "file_id": "FILE_1",
                            "service": "SER_1",
                            "service_nom": "Consultation",
                            "professionnel_nom": "Clinique Z",
                            "date_jour": "2026-04-20",
                            "temps_moyen_attente": 30,
                            "etat_file": "En_cours",
                            "nombre_clients": 8
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation",
                examples=[
                    OpenApiExample(
                        "Date manquante",
                        value={"error": "Le paramètre 'date' est obligatoire"}
                    ),
                    OpenApiExample(
                        "Format invalide",
                        value={"error": "Format de date invalide (YYYY-MM-DD)"}
                    )
                ]
            ),

            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Non autorisé",
                        value={"error": "Accès refusé à ce service"}
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Non trouvé",
                examples=[
                    OpenApiExample(
                        "Service introuvable",
                        value={"error": "Service introuvable"}
                    ),
                    OpenApiExample(
                        "File introuvable",
                        value={"error": "Aucune file d'attente pour cette date"}
                    )
                ]
            )
        }
    )
    def get(self, request, service_id):

        utilisateur = request.user

        #  récupérer professionnel connecté
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        

        #  récupérer date
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"error": "Le paramètre 'date' est obligatoire"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Format de date invalide (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  vérifier service appartient au professionnel
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

        #  récupérer file
        file = FileDattente.objects.select_related(
            "service",
            "professionnel"
        ).filter(
            service=service,
            date_jour=date_obj
        ).first()

        if not file:
            return Response(
                {"error": "Aucune file d'attente pour cette date"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FileDattenteSerializer(file)

        return Response(serializer.data, status=status.HTTP_200_OK)