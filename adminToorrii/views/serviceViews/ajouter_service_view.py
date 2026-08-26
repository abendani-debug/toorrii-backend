import json
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter
)
from drf_spectacular.types import OpenApiTypes

from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import ServiceSerializer
from adminToorrii.models import Professionnel


class AjouterServiceView(APIView):
    """
    Endpoint : Ajouter un service avec planning
    """

    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [IsAdminUserCustom]

    # =========================
    # SAFE JSON PARSER
    # =========================
    def safe_json(self, value):
        if isinstance(value, str):
            return json.loads(value)
        return value

    # =========================
    # SWAGGER DOC
    # =========================
    @extend_schema(
        tags=["Service"],
        summary="Ajouter un service",
        description="""
Créer un service avec :

-  Planning hebdomadaire (obligatoire)
-  Pauses (optionnel)
-  Exceptions (optionnel)
-  Image (optionnel)

 `planning` et `exceptions` doivent être envoyés en JSON (string).
""",
        parameters=[
            OpenApiParameter(
                name="professionnel_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="ID du professionnel"
            )
        ],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {

                    "nom_service": {"type": "string"},
                    "description": {"type": "string"},
                    "prix": {"type": "number"},
                    "duree_moyenne_creneau": {"type": "integer"},

                    "photo_principal": {
                        "type": "string",
                        "format": "binary"
                    },

                    "planning": {
                        "type": "string",
                        "description": "JSON du planning"
                    },

                    "exceptions": {
                        "type": "string",
                        "description": "JSON des exceptions"
                    }
                },
                "required": ["nom_service", "planning"]
            }
        },
        responses={
            201: OpenApiResponse(
                description="Service créé avec succès",
                response={
                    "type": "object",
                    "example": {
                        "message": "Service créé avec succès",
                        "data": {
                            "service_id": "SRV_1",
                            "nom_service": "Consultation",
                            "prix": 1500
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description="Erreur de validation",
                response={
                    "type": "object",
                    "example": {
                        "planning": "Format JSON invalide"
                    }
                }
            ),
            404: OpenApiResponse(
                description="Professionnel non trouvé",
                response={
                    "type": "object",
                    "example": {
                        "detail": "Not found."
                    }
                }
            )
        },
        examples=[
            OpenApiExample(
                "Exemple complet",
                summary="Créer un service",
                value={
                    "nom_service": "Consultation médicale",
                    "description": "Consultation générale",
                    "prix": 2000,
                    "duree_moyenne_creneau": 30,

                    "planning": json.dumps([
                        {
                            "nom_jour": "LUNDI",
                            "heure_debut_service": "08:00:00",
                            "heure_fin_service": "16:00:00",
                            "pauses": [
                                {
                                    "heure_debut_pause": "12:00:00",
                                    "heure_fin_pause": "13:00:00"
                                }
                            ]
                        }
                    ]),

                    "exceptions": json.dumps([
                        {
                            "date_debut_exception": "2026-04-20",
                            "date_fin_exception": "2026-04-20",
                            "heure_debut_exception": "10:00:00",
                            "heure_fin_exception": "12:00:00",
                            "motif": "Réunion"
                        }
                    ])
                },
                request_only=True
            )
        ]
    )

    # =========================
    # POST METHOD
    # =========================
    @transaction.atomic
    def post(self, request, professionnel_id):

        #  Récupérer professionnel
        professionnel = get_object_or_404(
            Professionnel,
            professionnel_id=professionnel_id
        )

        # =========================
        # PLANNING
        # =========================
        planning_raw = request.data.get("planning")

        if not planning_raw:
            return Response(
                {"planning": "Le champ planning est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            planning = self.safe_json(planning_raw)
        except json.JSONDecodeError:
            return Response(
                {"planning": "Format JSON invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # =========================
        # PARSE PAUSES
        # =========================
        for p in planning:
            if "pauses" in p and isinstance(p["pauses"], str):
                try:
                    p["pauses"] = json.loads(p["pauses"])
                except json.JSONDecodeError:
                    return Response(
                        {"pauses": "Format JSON invalide"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # =========================
        # EXCEPTIONS
        # =========================
        exceptions_raw = request.data.get("exceptions")
        exceptions = []

        if exceptions_raw:
            try:
                exceptions = self.safe_json(exceptions_raw)
            except json.JSONDecodeError:
                return Response(
                    {"exceptions": "Format JSON invalide"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # =========================
        # DATA CLEAN
        # =========================
        data = {
            key: request.data[key]
            for key in request.data
            if key not in ("planning", "exceptions")
        }

        data["planning"] = planning
        data["exceptions"] = exceptions

        if "photo_principal" in request.FILES:
            data["photo_principal"] = request.FILES["photo_principal"]

        # =========================
        # SERIALIZER
        # =========================
        serializer = ServiceSerializer(
            data=data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        service = serializer.save(professionnel=professionnel)

        # =========================
        # RESPONSE
        # =========================
        return Response(
            {
                "message": "Service créé avec succès",
                "data": ServiceSerializer(service).data
            },
            status=status.HTTP_201_CREATED
        )