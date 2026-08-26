from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import logging
from rest_framework.permissions import  AllowAny
from adminToorrii.models import AdminUser
from authentication.serializers import AdminResetPasswordRequestSerializer
from authentication.utils.professionnel_utils import send_reset_password_admin
from authentication.utils.professionnel_utils import generate_otp

logger = logging.getLogger(__name__)


class AdminResetPasswordRequestView(APIView):
    permission_classes = [AllowAny]
    """
    Demande un code OTP pour réinitialiser le mot de passe d’un administrateur.
    """

    @extend_schema(
        tags=["Authentification Admin"],
        summary="Demande de code OTP pour réinitialisation du mot de passe",
        description=(
            "Cet endpoint permet d’envoyer un code OTP (One-Time Password) "
            "à l’email de l’administrateur afin de réinitialiser son mot de passe.\n\n"
            " Règles de sécurité :\n"
            "- Maximum 3 demandes avant blocage temporaire\n"
            "- Blocage de 30 minutes après 3 tentatives\n"
            "- Un délai peut être imposé entre deux demandes"
        ),

        request=AdminResetPasswordRequestSerializer,

        responses={
            200: OpenApiResponse(
                description="Code OTP envoyé avec succès",
                response={
                    "type": "object",
                    "properties": {
                        "status": {"type": "boolean"},
                        "message": {"type": "string"},
                        "nombre_envoi": {"type": "integer"}
                    }
                }
            ),

            400: OpenApiResponse(
                description="Erreur (email invalide, utilisateur introuvable, délai non respecté)"
            ),

            500: OpenApiResponse(
                description="Erreur interne du serveur"
            )
        },

        examples=[
            #  Succès
            OpenApiExample(
                name="Succès",
                summary="OTP envoyé",
                value={
                    "status": True,
                    "message": "Code envoyé avec succès.",
                    "nombre_envoi": 1
                },
                response_only=True,
                status_codes=["200"]
            ),

            #  Email invalide
            OpenApiExample(
                name="Email invalide",
                summary="Erreur de validation",
                value={
                    "status": False,
                    "email": {
                        "email": ["Enter a valid email address."]
                    }
                },
                response_only=True,
                status_codes=["400"]
            ),

            #  Utilisateur introuvable
            OpenApiExample(
                name="Utilisateur introuvable",
                summary="Email inexistant",
                value={
                    "status": False,
                    "message": "Aucun compte administrateur avec cet email."
                },
                response_only=True,
                status_codes=["400"]
            ),

            #  Délai non respecté
            OpenApiExample(
                name="Délai non respecté",
                summary="Blocage temporaire",
                value={
                    "status": False,
                    "message": "Vous ne pouvez pas demander un nouveau code pour le moment. Réessayez dans 10 min 30 sec."
                },
                response_only=True,
                status_codes=["400"]
            ),

            #  Erreur serveur
            OpenApiExample(
                name="Erreur serveur",
                summary="Erreur interne",
                value={
                    "status": False,
                    "message": "Une erreur interne est survenue."
                },
                response_only=True,
                status_codes=["500"]
            ),

            #  Exemple de requête
            OpenApiExample(
                name="Exemple requête",
                summary="Body envoyé",
                value={
                    "email": "admin@example.com"
                },
                request_only=True
            ),
        ]
    )
    def post(self, request):
        serializer = AdminResetPasswordRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": False, "email": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']

        try:
            admin = AdminUser.objects.get(email=email)
        except AdminUser.DoesNotExist:
            return Response(
                {"status": False, "message": "Aucun compte administrateur avec cet email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()

        #  Vérification du délai
        if admin.temp_code_verification_reset_password and admin.temp_code_verification_reset_password > now:
            remaining = admin.temp_code_verification_reset_password - now
            minutes = remaining.seconds // 60
            seconds = remaining.seconds % 60

            return Response({
                "status": False,
                "message": f"Vous ne pouvez pas demander un nouveau code pour le moment. Réessayez dans {minutes} min {seconds} sec."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp = generate_otp()
            admin.code_verification_reset_password = otp
            admin.nombre_send_email_reset_password += 1

            #  Blocage après 3 tentatives
            if admin.nombre_send_email_reset_password >= 3:
                admin.temp_code_verification_reset_password = now + timedelta(minutes=30)

            admin.save()

            send_reset_password_admin(
                email=admin.email,
                nom=admin.nom,
                otp=otp
            )

            return Response({
                "status": True,
                "message": "Code envoyé avec succès.",
                "nombre_envoi": admin.nombre_send_email_reset_password
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Erreur AdminResetPasswordRequestView : %s", str(e))
            return Response({
                "status": False,
                "message": "Une erreur interne est survenue."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)