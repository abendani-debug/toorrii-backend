from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from authentication.serializers import ProfessionnelRegisterSerializer
from adminToorrii.models import Professionnel
import logging
from rest_framework.permissions import  AllowAny


logger = logging.getLogger(__name__)


class ProfessionnelRegisterView(APIView):
    permission_classes = [AllowAny]
    """
    Endpoint pour l'inscription d'un professionnel.
    """

    @extend_schema(
        tags=["Authentification Professionnel"],
        summary="Créer un compte professionnel",
        description=(
            "Permet à un professionnel de créer un compte sur la plateforme.\n\n"
            "**Notes :**\n"
            "- Les champs `professionnel_id`, `etat_compte`, `compte_verification`, "
            "`date_inscription`, `nombre_priorite`, `date_creation` ne doivent pas être envoyés.\n"
            "- Un email avec un OTP est envoyé automatiquement après la création.\n"
            "- Si l'email existe déjà, retourne une erreur 400."
        ),
        request=ProfessionnelRegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="Professionnel créé avec succès et OTP envoyé",
                examples=[
                    OpenApiExample(
                        "Réponse 201",
                        summary="Succès",
                        value={
                            "status": True,
                            "message": "Professionnel enregistré avec succès. Un OTP a été envoyé à votre email.",
                            "data": {
                                "professionnel_id": "pro_15",
                                "nom_entreprise": "Clinique Oran",
                                "email": "contact@clinique.dz",
                                "nombre_send_email": 1
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Erreur de validation (email déjà existant ou champs invalides)",
                examples=[
                    OpenApiExample(
                        "Réponse 400",
                        summary="Email existant",
                        value={
                            "status": False,
                            "message": "Un compte avec cet email existe déjà."
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne du serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        summary="Erreur serveur",
                        value={
                            "status": False,
                            "error": "Une erreur interne est survenue. Veuillez réessayer plus tard."
                        }
                    )
                ]
            )
        }
    )
    def post(self, request):
        try:
            serializer = ProfessionnelRegisterSerializer(data=request.data)

            if serializer.is_valid():
                professionnel = serializer.save()

                return Response({
                    "status": True,
                    "message": "Professionnel enregistré avec succès. Un OTP a été envoyé à votre email.",
                    "data": {
                        "professionnel_id": professionnel.professionnel_id,
                        "nom_entreprise": professionnel.nom_entreprise,
                        "email": professionnel.email,
                        "nombre_send_email": professionnel.nombre_send_email,
                    }
                }, status=status.HTTP_201_CREATED)

            # Gestion des erreurs de validation
            logger.error("Erreurs de validation ProfessionnelRegisterView : %s", serializer.errors)
            # Extraire le premier message d'erreur lisible
            first_message = None
            for field_errors in serializer.errors.values():
                if isinstance(field_errors, list) and field_errors:
                    first_message = str(field_errors[0])
                    break
            return Response({
                "status": False,
                "message": first_message or "Données invalides.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error("Erreur interne dans ProfessionnelRegisterView : %s", str(e))
            return Response({
                "status": False,
                "error": "Une erreur interne est survenue. Veuillez réessayer plus tard."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)