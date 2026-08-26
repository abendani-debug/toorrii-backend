import json
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers

from drf_spectacular.utils import extend_schema, OpenApiExample

from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import Service
from professionnel.serializers import ServiceSerializer, ServiceDetailSerializer


class AjouterServiceView(APIView):
    """
    POST - Créer un service pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        tags=["Services - Professionnel"],
        summary="Créer un service",
        description="""
        Création d’un service avec :
        - planning obligatoire
        - pauses
        - exceptions optionnelles

        Format :
        - multipart/form-data
        - planning & exceptions = JSON string
        """,
        request=ServiceSerializer,
        examples=[
            OpenApiExample(
                "Exemple request",
                value={
                    "nom_service": "Massage Relaxant",
                    "prix_service": 2500,
                    "duree_moyenne_creneau": 30,
                    "planning": [
                        {
                            "nom_jour": "LUNDI",
                            "heure_debut_service": "08:00",
                            "heure_fin_service": "16:00",
                            "pauses": [
                                {
                                    "description": "Pause déjeuner",
                                    "heure_debut_pause": "12:00",
                                    "heure_fin_pause": "13:00"
                                }
                            ]
                        }
                    ],
                    "exceptions": []
                }
            )
        ]
    )
    @transaction.atomic
    def post(self, request):
        try:
            # 1 professionnel connecté
            professionnel = request.user.professionnel_profile

            #  Convertir QueryDict -> dict simple
            data = {key: request.data.get(key) for key in request.data.keys()}

            #  Parser planning (obligatoire)
            planning_raw = data.get("planning")
            if planning_raw:
                try:
                    data["planning"] = json.loads(planning_raw)
                except json.JSONDecodeError:
                    return Response(
                        {"planning": "Format JSON invalide"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"planning": "Le champ planning est requis"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Parser exceptions (optionnel)
            exceptions_raw = data.get("exceptions")
            if exceptions_raw:
                try:
                    data["exceptions"] = json.loads(exceptions_raw)
                except json.JSONDecodeError:
                    return Response(
                        {"exceptions": "Format JSON invalide"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            #  Conversion des types
            if "prix_service" in data:
                data["prix_service"] = float(data["prix_service"])
            if "duree_moyenne_creneau" in data:
                data["duree_moyenne_creneau"] = int(data["duree_moyenne_creneau"])

            #  Serializer
            serializer = ServiceSerializer(
                data=data,
                context={"request": request}
            )

            if not serializer.is_valid():
                return Response(
                    {
                        "message": "Erreur de validation",
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Sauvegarde avec professionnel
            service = serializer.save(professionnel=professionnel)

            return Response(
                {
                    "message": "Service créé avec succès",
                    "data": ServiceDetailSerializer(service, context={"request": request}).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {
                    "message": "Erreur interne du serveur",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )