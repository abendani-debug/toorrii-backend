from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsProfessionnelUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from adminToorrii.models import Professionnel
from adminToorrii.utils.brevo_service import send_professionnel_demande_désactivation_compte
import logging

logger = logging.getLogger(__name__)

class ProfessionnelDemandeDesactivationCompteView(APIView):
    """
    Endpoint pour demander la désactivation du compte professionnel actuel.
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Compte Professionnel"],
        summary="Demander la désactivation du compte",
        description=(
            "Permet à un professionnel connecté de demander la désactivation de son compte.\n\n"
            "L'email de demande sera envoyé à l'administration Toorrii.\n"
            "Vérifie que l'utilisateur connecté est un professionnel."
        ),
        responses={
            200: OpenApiResponse(
                description="Demande envoyée avec succès",
                examples=[OpenApiExample(
                    name="Succès",
                    value={"status": True, "message": "Votre demande de désactivation a été envoyée à l'administration."},
                    response_only=True
                )]
            ),
            403: OpenApiResponse(
                description="Utilisateur non autorisé",
                examples=[OpenApiExample(
                    name="Non-professionnel",
                    value={"status": False, "message": "Vous n'êtes pas autorisé à effectuer cette action."},
                    response_only=True
                )]
            ),
            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[OpenApiExample(
                    name="Erreur serveur",
                    value={"status": False, "message": "Une erreur interne est survenue."},
                    response_only=True
                )]
            )
        }
    )
    def post(self, request):
        user = request.user

        # Vérifier que l'utilisateur est un professionnel
        if not hasattr(user, "professionnel_profile"):
            return Response(
                {"status": False, "message": "Vous n'êtes pas autorisé à effectuer cette action."},
                status=status.HTTP_403_FORBIDDEN
            )

        professionnel = user.professionnel_profile

        try:
            # Envoi de l'email à l'administration
            send_professionnel_demande_désactivation_compte(
                email=user.email,
                nom=professionnel.nom_entreprise if hasattr(professionnel, "nom_entreprise") else "Professionnel"
            )
        except Exception as e:
            logger.error("Erreur lors de l'envoi de l'email de désactivation: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"status": True, "message": "Votre demande de désactivation a été envoyée à l'administration."},
            status=status.HTTP_200_OK
        )