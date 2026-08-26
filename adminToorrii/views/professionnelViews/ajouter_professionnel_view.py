import logging
from django.db import IntegrityError, transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema, OpenApiResponse

from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import ProfessionnelSerializer
from adminToorrii.utils.brevo_service import send_professionnel_notification

logger = logging.getLogger(__name__)


class AjouterProfessionnelView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Professionnels"],
        summary="Ajouter un professionnel",
        description="Crée un professionnel et envoie une notification email (non bloquante).",
        request=ProfessionnelSerializer,
        responses={
            201: OpenApiResponse(description="Professionnel créé avec succès"),
            400: OpenApiResponse(description="Erreur de validation"),
            409: OpenApiResponse(description="Conflit de données"),
            500: OpenApiResponse(description="Erreur serveur"),
        }
    )
    def post(self, request):
        serializer = ProfessionnelSerializer(data=request.data)

        try:
            # -----------------------------
            # Validation des données
            # -----------------------------
            serializer.is_valid(raise_exception=True)

            # -----------------------------
            # Sauvegarde DB (transaction)
            # -----------------------------
            with transaction.atomic():
                professionnel = serializer.save()

            email_sent = True

            return Response(
                {
                    "status": True,
                    "message": "Professionnel créé avec succès.",
                    "email_sent": email_sent,
                    "data": ProfessionnelSerializer(professionnel).data
                },
                status=status.HTTP_201_CREATED
            )

        # -----------------------------
        # ERREURS DE VALIDATION (400)
        # -----------------------------
        except ValidationError as e:
            logger.info(
                "Erreur validation AjouterProfessionnel | %s",
                e.detail
            )
            return Response(
                {
                    "status": False,
                    "error_type": "VALIDATION_ERROR",
                    "errors": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # ERREURS DB (CONFLIT)
        # -----------------------------
        except IntegrityError as e:
            logger.warning(
                "Conflit DB AjouterProfessionnel | %s",
                str(e)
            )
            return Response(
                {
                    "status": False,
                    "error_type": "DATABASE_CONFLICT",
                    "message": "Un professionnel avec ces informations existe déjà."
                },
                status=status.HTTP_409_CONFLICT
            )

        # -----------------------------
        # ERREUR SERVEUR INATTENDUE
        # -----------------------------
        except Exception as e:
            logger.error(
                "Erreur serveur AjouterProfessionnel",
                exc_info=True
            )
            return Response(
                {
                    "status": False,
                    "error_type": "INTERNAL_SERVER_ERROR",
                    "message": "Une erreur interne est survenue. Veuillez réessayer plus tard."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
