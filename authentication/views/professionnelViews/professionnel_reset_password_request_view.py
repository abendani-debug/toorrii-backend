from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import logging
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from adminToorrii.models import Professionnel
from authentication.serializers import ProfessionnelResetPasswordRequestSerializer
from authentication.utils.professionnel_utils import generate_otp, send_reset_password_professionnel
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

class ProfessionnelResetPasswordRequestView(APIView):
    permission_classes = [AllowAny]
    """
    Endpoint pour demander un code de réinitialisation de mot de passe pour un compte professionnel.
    """

    @extend_schema(
        tags=["Authentification Professionnel"],
        summary="Demande de réinitialisation de mot de passe",
        description=(
            "Génère un OTP de réinitialisation, le stocke et l'envoie par email.\n"
            "Le code est valide 15 minutes."
        ),
        request=ProfessionnelResetPasswordRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="OTP envoyé avec succès",
                examples=[OpenApiExample(
                    "Réponse succès",
                    value={
                        "status": True,
                        "message": "Code OTP envoyé par email.",
                        "nombre_envoi": 1
                    }
                )]
            ),
            400: OpenApiResponse(
                description="Email invalide ou introuvable",
                examples=[OpenApiExample(
                    "Réponse erreur",
                    value={
                        "status": False,
                        "message": "Aucun compte professionnel avec cet email."
                    }
                )]
            ),
            500: OpenApiResponse(
                description="Erreur interne serveur",
                examples=[OpenApiExample(
                    "Réponse erreur serveur",
                    value={
                        "status": False,
                        "message": "Erreur lors de l'envoi du code OTP."
                    }
                )]
            )
        }
    )
    def post(self, request):
        serializer = ProfessionnelResetPasswordRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": False, "email": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        try:
            professionnel = Professionnel.objects.get(email=email)
        except Professionnel.DoesNotExist:
            return Response({"status": False, "message": "Aucun compte professionnel avec cet email."},
                            status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()

        # Vérifier si blocage temporaire
        if professionnel.temp_code_verification_reset_password and professionnel.temp_code_verification_reset_password > now:
            remaining = professionnel.temp_code_verification_reset_password - now
            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60
            return Response({
                "status": False,
                "message": f"Vous ne pouvez pas demander un nouveau code pour le moment. Réessayez dans {minutes} min {seconds} sec."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Générer OTP
            otp = generate_otp()
            professionnel.code_verification_reset_password = otp
            professionnel.nombre_send_email_reset_password += 1

            # Si atteint 3 envois, bloquer 30 min
            if professionnel.nombre_send_email_reset_password >= 3:
                professionnel.temp_code_verification_reset_password = now + timedelta(minutes=30)

            professionnel.save()

            # Envoyer email
            send_reset_password_professionnel(
                email=professionnel.email,
                nom_entreprise=professionnel.nom_entreprise,
                otp=otp
            )

            return Response({
                "status": True,
                "message": "Code envoyé avec succès.",
                "nombre_envoi": professionnel.nombre_send_email_reset_password
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Erreur ProfessionnelResetPasswordRequestView : %s", str(e))
            return Response({
                "status": False,
                "message": "Une erreur interne est survenue."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)