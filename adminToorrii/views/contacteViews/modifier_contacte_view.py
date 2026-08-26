from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.exceptions import ValidationError

from adminToorrii.models import Contacte
from adminToorrii.serializers import ContacteAdminSerializer
from adminToorrii.permissions import IsAdminUserCustom

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample
)

import logging

logger = logging.getLogger(__name__)


class ModifierContacteView(APIView):
    """
    PUT /api/contact/modifier/
    Modifier le contact unique (Admin uniquement)
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Contacte"],
        summary="Modifier le contact unique",
        description=(
            "Met à jour les informations du contact unique.\n\n"
            " Accès réservé aux administrateurs.\n"
            " Mise à jour partielle autorisée.\n"
            " Une seule instance existe dans la base."
        ),
        request=ContacteAdminSerializer,
        responses={
            200: OpenApiResponse(
                description="Contact mis à jour avec succès",
                response=ContacteAdminSerializer,
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "message": "Contact mis à jour avec succès",
                            "data": {
                                "contacte_id": "CONTACT_1",
                                "email": "new@toorrii.com"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Données invalides",
                examples=[
                    OpenApiExample(
                        "Réponse 400",
                        value={
                            "status": False,
                            "errors": {
                                "email": ["Email invalide"]
                            }
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={
                            "status": False,
                            "message": "Permission refusée."
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Contact introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={
                            "status": False,
                            "message": "Aucun contact trouvé pour mise à jour."
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={
                            "status": False,
                            "message": "Erreur interne serveur."
                        }
                    )
                ]
            ),
        }
    )
    def put(self, request):
        try:
            #  Récupération du singleton
            contact = Contacte.objects.first()

            if not contact:
                return Response(
                    {"status": False, "message": "Aucun contact trouvé pour mise à jour."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = ContacteAdminSerializer(
                contact,
                data=request.data,
                partial=True
            )

            #  Validation
            if not serializer.is_valid():
                return Response(
                    {"status": False, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Transaction DB
            with transaction.atomic():
                serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Contact mis à jour avec succès",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response(
                {"status": False, "errors": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error("Erreur ModifierContacteView PUT: %s", str(e))
            return Response(
                {"status": False, "message": "Erreur interne serveur."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )