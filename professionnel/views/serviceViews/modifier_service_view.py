import json
import logging
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiParameter
)

from adminToorrii.models import Service
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import ServiceSerializer, ServiceDetailSerializer

logger = logging.getLogger(__name__)


class ModifierServiceView(APIView):
    """
    PUT - Modifier un service (professionnel connecté)
    """

    permission_classes = [IsProfessionnelUserCustom]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @extend_schema(
        tags=["Services - Professionnel"],
        summary="Modifier un service",
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True
            )
        ],
        request=ServiceSerializer,
        examples=[
            OpenApiExample(
                "Exemple update service",
                value={
                    "nom_service": "Massage Premium",
                    "prix_service": 3000,
                    "planning": [
                        {
                            "nom_jour": "LUNDI",
                            "heure_debut_service": "09:00",
                            "heure_fin_service": "18:00",
                            "pauses": [
                                {
                                    "pause_id": "PLNP_1",
                                    "description": "Pause modifiée",
                                    "heure_debut_pause": "12:30",
                                    "heure_fin_pause": "13:30"
                                }
                            ]
                        }
                    ],
                    "exceptions": [
                        {
                            "exception_id": "PLNE_1",
                            "raison": "Congé"
                        }
                    ]
                }
            )
        ]
    )
    @transaction.atomic
    def put(self, request, service_id):
        try:
            # -------------------------
            # 1. USER PROFESSIONNEL
            # -------------------------
            try:
                professionnel = request.user.professionnel_profile
            except Exception:
                return Response(
                    {"error": "Utilisateur non professionnel"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # -------------------------
            # 2. GET SERVICE (SECURE)
            # -------------------------
            try:
                service = Service.objects.get(
                    service_id=service_id,
                    professionnel=professionnel
                )
            except Service.DoesNotExist:
                return Response(
                    {"error": "Service introuvable ou non autorisé"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # -------------------------
            # 3. QUERYDICT → DICT
            # -------------------------
            data = {key: request.data.get(key) for key in request.data.keys()}

            # -------------------------
            # 4. PARSE JSON planning
            # -------------------------
            if "planning" in data and data["planning"]:
                try:
                    data["planning"] = json.loads(data["planning"])
                except json.JSONDecodeError:
                    return Response(
                        {"planning": "Format JSON invalide"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # -------------------------
            # 5. PARSE JSON exceptions
            # -------------------------
            if "exceptions" in data and data["exceptions"]:
                try:
                    data["exceptions"] = json.loads(data["exceptions"])
                except json.JSONDecodeError:
                    return Response(
                        {"exceptions": "Format JSON invalide"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # -------------------------
            # 6. TYPE CONVERSION
            # -------------------------
            if "prix_service" in data and data["prix_service"] is not None:
                data["prix_service"] = float(data["prix_service"])

            if "duree_moyenne_creneau" in data and data["duree_moyenne_creneau"] is not None:
                data["duree_moyenne_creneau"] = int(data["duree_moyenne_creneau"])

            # -------------------------
            # 7. IMAGE
            # -------------------------
            if "photo_principal" in request.FILES:
                data["photo_principal"] = request.FILES["photo_principal"]

            # -------------------------
            # 8. SERIALIZER UPDATE
            # -------------------------
            serializer = ServiceSerializer(
                service,
                data=data,
                partial=True,
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

            service_updated = serializer.save()

            # -------------------------
            # 9. RESPONSE
            # -------------------------
            return Response(
                {
                    "message": "Service modifié avec succès",
                    "data": ServiceDetailSerializer(
                        service_updated,
                        context={"request": request}
                    ).data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Erreur ModifierServiceView: {str(e)}")
            return Response(
                {
                    "message": "Erreur interne serveur",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )