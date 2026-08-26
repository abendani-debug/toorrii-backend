from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from adminToorrii.models import Professionnel
from authentication.serializers import ProfessionnelResetPasswordVerifySerializer
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

class ProfessionnelResetPasswordVerifyView(APIView):
    """
    Endpoint pour vérifier le code OTP et réinitialiser le mot de passe d’un professionnel.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentification Professionnel"],
        summary="Vérifier OTP et réinitialiser mot de passe",
        description=(
            "Permet de vérifier le code OTP envoyé par email et de définir un nouveau mot de passe.\n\n"
            " Sécurité :\n"
            "- Vérification CSRF obligatoire (cookie + header)\n"
            "- OTP valide requis\n\n"
            " Champs requis :\n"
            "- email\n"
            "- otp\n"
            "- new_password"
        ),
        request=ProfessionnelResetPasswordVerifySerializer,
        responses={
            200: OpenApiResponse(
                description="Mot de passe réinitialisé avec succès",
                examples=[
                    OpenApiExample(
                        name="Succès",
                        summary="Réinitialisation réussie",
                        value={
                            "status": True,
                            "message": "Mot de passe réinitialisé avec succès."
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Erreur de validation ou OTP incorrect",
                examples=[
                    OpenApiExample(
                        name="OTP incorrect",
                        value={
                            "status": False,
                            "message": "Code OTP incorrect."
                        },
                        response_only=True
                    ),
                    OpenApiExample(
                        name="Email introuvable",
                        value={
                            "status": False,
                            "message": "Compte professionnel introuvable."
                        },
                        response_only=True
                    ),
                    OpenApiExample(
                        name="Erreur validation",
                        value={
                            "email": ["Ce champ est obligatoire."],
                            "otp": ["Ce champ est obligatoire."],
                            "new_password": ["Ce champ est obligatoire."]
                        },
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description="CSRF token invalide",
                examples=[
                    OpenApiExample(
                        name="CSRF invalide",
                        value={"error": "Invalid CSRF Token"},
                        response_only=True
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur serveur interne",
                examples=[
                    OpenApiExample(
                        name="Erreur serveur",
                        value={"error": "Une erreur interne est survenue."},
                        response_only=True
                    )
                ]
            )
        }
    )
    def post(self, request):
        # --- Validation des données ---
        serializer = ProfessionnelResetPasswordVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            professionnel = Professionnel.objects.get(email=email)
        except Professionnel.DoesNotExist:
            return Response({
                "status": False,
                "message": "Compte professionnel introuvable."
            }, status=status.HTTP_400_BAD_REQUEST)

        # --- Vérification OTP ---
        if professionnel.code_verification_reset_password != otp:
            return Response({
                "status": False,
                "message": "Code OTP incorrect."
            }, status=status.HTTP_400_BAD_REQUEST)

        # --- Mise à jour du mot de passe de l'utilisateur lié ---
        utilisateur = professionnel.utilisateur
        utilisateur.set_password(new_password)
        utilisateur.save(update_fields=['password'])

        # --- Reset des champs OTP dans Professionnel ---
        professionnel.code_verification_reset_password = None
        professionnel.temp_code_verification_reset_password = None
        professionnel.nombre_send_email_reset_password = 0
        professionnel.save(update_fields=[
            'code_verification_reset_password',
            'temp_code_verification_reset_password',
            'nombre_send_email_reset_password'
        ])

        return Response({
            "status": True,
            "message": "Mot de passe réinitialisé avec succès."
        }, status=status.HTTP_200_OK)