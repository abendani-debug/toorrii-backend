from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import logging
from rest_framework.permissions import  AllowAny
from adminToorrii.models import AdminUser
from authentication.serializers import AdminResetPasswordVerifySerializer


logger = logging.getLogger(__name__)



class AdminResetPasswordVerifyView(APIView):
    permission_classes = [AllowAny]
    """
    Vérifie le code OTP et réinitialise le mot de passe
    pour l'admin et son utilisateur lié.
    """

    @extend_schema(
        tags=["Authentification Admin"],
        summary="Vérification OTP et réinitialisation du mot de passe",
        description=(
            "Cet endpoint permet de vérifier le code OTP envoyé par email "
            "et de définir un nouveau mot de passe pour l'administrateur "
            "ainsi que pour l'utilisateur lié.\n\n"
            " Protection CSRF requise :\n"
            "- Cookie : csrftoken\n"
            "- Header : X-CSRFToken"
        ),
        request=AdminResetPasswordVerifySerializer,
        responses={
            200: OpenApiResponse(
                description="Mot de passe réinitialisé avec succès",
                response={
                    "type": "object",
                    "properties": {
                        "status": {"type": "boolean"},
                        "message": {"type": "string"}
                    }
                }
            ),
            400: OpenApiResponse(
                description="Erreur (OTP invalide, utilisateur introuvable, données invalides)"
            ),
            403: OpenApiResponse(
                description="Token CSRF invalide"
            )
        },
        examples=[
            OpenApiExample(
                name="Succès",
                value={
                    "status": True,
                    "message": "Mot de passe réinitialisé avec succès."
                },
                response_only=True,
                status_codes=["200"]
            ),
            OpenApiExample(
                name="OTP incorrect",
                value={
                    "status": False,
                    "message": "Code OTP incorrect."
                },
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Utilisateur introuvable",
                value={
                    "status": False,
                    "message": "Compte introuvable."
                },
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Erreur CSRF",
                value={
                    "error": "Invalid CSRF Token"
                },
                response_only=True,
                status_codes=["403"]
            ),
            OpenApiExample(
                name="Exemple requête",
                value={
                    "email": "admin@example.com",
                    "otp": "123456",
                    "new_password": "MotDePasseFort123!"
                },
                request_only=True
            ),
        ]
    )
    def post(self, request):
        #  Vérification CSRF
        csrf_cookie = request.COOKIES.get("csrftoken")
        csrf_header = request.headers.get("X-CSRFToken")

        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return Response(
                {"error": "Invalid CSRF Token"},
                status=status.HTTP_403_FORBIDDEN
            )

        #  Validation des données
        serializer = AdminResetPasswordVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            #  Optimisation : récupération avec utilisateur lié
            admin = AdminUser.objects.select_related('utilisateur').get(email=email)
        except AdminUser.DoesNotExist:
            return Response(
                {"status": False, "message": "Compte introuvable."},
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Vérification OTP
        if admin.code_verification_reset_password != otp:
            return Response(
                {"status": False, "message": "Code OTP incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            #  Transaction sécurisée
            with transaction.atomic():

                #  Mise à jour mot de passe Admin
                admin.set_password(new_password)

                #  Mise à jour mot de passe Utilisateur lié
                if hasattr(admin, 'utilisateur') and admin.utilisateur:
                    admin.utilisateur.set_password(new_password)
                    admin.utilisateur.save()

                #  Reset OTP
                admin.code_verification_reset_password = None
                admin.temp_code_verification_reset_password = None
                admin.nombre_send_email_reset_password = 0

                admin.save(update_fields=[
                    'password',
                    'code_verification_reset_password',
                    'temp_code_verification_reset_password',
                    'nombre_send_email_reset_password'
                ])

        except Exception as e:
            logger.error(f"Erreur reset password: {str(e)}")
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "status": True,
                "message": "Mot de passe réinitialisé avec succès."
            },
            status=status.HTTP_200_OK
        )