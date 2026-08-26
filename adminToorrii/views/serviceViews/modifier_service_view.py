import json
import logging

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

from adminToorrii.models import Service
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import ServiceSerializer, ServiceDetailSerializer

logger = logging.getLogger(__name__)


class ModifierServiceView(APIView):
    """
    Endpoint : Modifier un service existant
    """

    permission_classes = [IsAdminUserCustom]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    # =========================
    # SAFE JSON
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
        summary="Modifier un service",
        description="""
Permet de modifier un service existant.

 Champs modifiables partiellement  
 Planning (optionnel)  
 Pauses (optionnel, imbriqué)  
 Exceptions (optionnel)  
 Image (optionnel)  

 `planning` et `planning_exception` doivent être envoyés en JSON string si présents.
""",
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="ID du service à modifier"
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
                        "description": "JSON du planning (optionnel)"
                    },

                    "planning_exception": {
                        "type": "string",
                        "description": "JSON des exceptions (optionnel)"
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="Service modifié avec succès",
                response={
                    "type": "object",
                    "example": {
                        "message": "Service modifié avec succès",
                        "data": {
                            "service_id": "SRV_1",
                            "nom_service": "Consultation mise à jour",
                            "prix": 2500
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
                description="Service non trouvé",
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
                "Exemple modification simple",
                summary="Modifier quelques champs",
                value={
                    "nom_service": "Consultation VIP",
                    "prix": 3000
                },
                request_only=True
            ),
            OpenApiExample(
                "Exemple avec planning",
                summary="Modifier planning et pauses",
                value={
                    "planning": json.dumps([
                        {
                            "nom_jour": "LUNDI",
                            "heure_debut_service": "09:00:00",
                            "heure_fin_service": "17:00:00",
                            "pauses": [
                                {
                                    "heure_debut_pause": "13:00:00",
                                    "heure_fin_pause": "14:00:00"
                                }
                            ]
                        }
                    ])
                },
                request_only=True
            )
        ]
    )

    # =========================
    # PUT METHOD
    # =========================
    @transaction.atomic
    def put(self, request, service_id):

        #  Récupérer service
        service = get_object_or_404(Service, service_id=service_id)

        # =========================
        # PARSE PLANNING (OPTIONAL)
        # =========================
        planning = None
        planning_raw = request.data.get("planning")

        if planning_raw:
            try:
                planning = self.safe_json(planning_raw)
            except json.JSONDecodeError:
                return Response(
                    {"planning": "Format JSON invalide"},
                    status=status.HTTP_400_BAD_REQUEST
                )

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
        # PARSE EXCEPTIONS
        # =========================
        planning_exception = None
        exceptions_raw = request.data.get("exceptions")

        if exceptions_raw:
            try:
                planning_exception = self.safe_json(exceptions_raw)
            except json.JSONDecodeError:
                return Response(
                    {"planning_exception": "Format JSON invalide"},
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

        if planning is not None:
            data["planning"] = planning

        if planning_exception is not None:
            data["exceptions"] = planning_exception

        if "photo_principal" in request.FILES:
            data["photo_principal"] = request.FILES["photo_principal"]

        # =========================
        # SERIALIZER
        # =========================
        serializer = ServiceSerializer(
            service,
            data=data,
            partial=True,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        # =========================
        # REFRESH + RESPONSE
        # =========================
        service.refresh_from_db()

        return Response(
            {
                "message": "Service modifié avec succès",
                "data": ServiceDetailSerializer(service).data
            },
            status=status.HTTP_200_OK
        )