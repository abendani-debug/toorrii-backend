from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import Contacte
from adminToorrii.serializers import ContacteAdminSerializer as ContacteSerializer
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class AjouterContacteView(APIView):
    """
    POST /api/contact/ajouter/
    Endpoint pour créer le contact unique. Seuls les admins peuvent ajouter un contact.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Contacte"],
        summary="Créer le contact unique (Admin uniquement)",
        description=(
            "Crée le contact unique de l'application.\n\n"
            " Il ne peut y avoir qu’un seul enregistrement Contacte.\n"
            "Seuls les utilisateurs admin peuvent effectuer cette action."
        ),
        request=ContacteSerializer,
        responses={
            201: OpenApiResponse(
                description="Contact créé avec succès",
                response=ContacteSerializer(many=False),
                examples=[
                    OpenApiExample(
                        "Réponse 201",
                        value={
                            "status": True,
                            "message": "Contact créé avec succès",
                            "data": {
                                "id": 1,
                                "email": "contact@toorrii.com",
                                "telephone_1": "+213600000000",
                                "telephone_2": "+213610000000",
                                "telephone_fixe": "021000000",
                                "adresse": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "ville": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "wilaya": {"fr": "Alger", "en": "Algiers", "ar": "الجزائر"},
                                "horaires": "08:00 - 18:00",
                                "site_web": "https://toorrii.com",
                                "facebook": "https://facebook.com/toorrii",
                                "instagram": None,
                                "tiktok": None,
                                "linkedin": None,
                                "x": None,
                                "message_acceuil": {"fr": "Bienvenue", "en": "Welcome", "ar": "مرحبا"},
                                "date_creation": "2025-12-20T14:00:00Z",
                                "historique_modifications": []
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Un contact existe déjà ou données invalides",
                examples=[
                    OpenApiExample(
                        "Réponse 400",
                        value={
                            "status": False,
                            "message": "Un contact existe déjà. Vous ne pouvez pas en créer un autre."
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Accès refusé pour les utilisateurs non-admin",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={
                            "status": False,
                            "message": "Vous n’avez pas les permissions nécessaires pour effectuer cette action."
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne du serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={
                            "status": False,
                            "message": "Une erreur interne est survenue."
                        }
                    )
                ]
            ),
        }
    )
    def post(self, request):
        try:
            # Vérifier s’il existe déjà un enregistrement
            if Contacte.objects.exists():
                return Response(
                    {"status": False, "message": "Un contact existe déjà. Vous ne pouvez pas en créer un autre."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ContacteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "message": "Contact créé avec succès", "data": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            return Response(
                {"status": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Erreur dans AjouterContacteView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
