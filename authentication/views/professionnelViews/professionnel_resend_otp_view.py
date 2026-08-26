from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
import logging
from rest_framework.permissions import  AllowAny

from adminToorrii.models import Professionnel
from authentication.serializers import ProfessionnelResendOTPSerializer
from authentication.utils.professionnel_utils import generate_otp, send_register_notification_professionnel

logger = logging.getLogger(__name__)


class ProfessionnelResendOTPView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        
        tags=["Authentification Professionnel"],
        summary="Renvoi du code de vérification OTP",
        description="""
Permet à un professionnel de demander un nouveau **code OTP de vérification d’email**.

### Règles de sécurité

Le système limite le nombre d'envois pour éviter les abus.

### Vérification du blocage

Avant l'envoi :

- si `temp_code_verification` est **NULL** → envoi autorisé
- si `temp_code_verification <= maintenant` → envoi autorisé
- si `temp_code_verification > maintenant` → envoi bloqué

### Gestion du compteur

| nombre_send_email | Action |
|---|---|
| 0 | envoi du code |
| 1 | envoi du code |
| ≥2 | envoi + blocage 30 minutes |

### Actions effectuées

- Génération d’un **OTP aléatoire**
- Mise à jour du champ `code_verification`
- Incrémentation du compteur `nombre_send_email`
- Envoi du code par **email**
""",
        request=ProfessionnelResendOTPSerializer,
        responses={
            200: OpenApiResponse(
                description="Code OTP envoyé avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "status": True,
                            "message": "Code envoyé avec succès.",
                            "nombre_envoi": 2
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Blocage temporaire",
                examples=[
                    OpenApiExample(
                        "Blocage OTP",
                        value={
                            "status": False,
                            "message": "Vous ne pouvez pas demander un nouveau code pour le moment. Réessayez dans 10 min 20 sec."
                        }
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Compte introuvable",
                examples=[
                    OpenApiExample(
                        "Email introuvable",
                        value={
                            "status": False,
                            "message": "Aucun compte professionnel avec cet email."
                        }
                    )
                ]
            ),

            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        "Erreur serveur",
                        value={
                            "status": False,
                            "message": "Une erreur interne est survenue."
                        }
                    )
                ]
            ),
        },

        examples=[
            OpenApiExample(
                "Exemple de requête",
                summary="Renvoi OTP",
                request_only=True,
                value={
                    "email": "contact@clinique-dz.com"
                }
            )
        ]
    )
    def post(self, request):

        try:

            serializer = ProfessionnelResendOTPSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data["email"]

            try:
                professionnel = Professionnel.objects.get(email=email)
            except Professionnel.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Aucun compte professionnel avec cet email."
                }, status=status.HTTP_404_NOT_FOUND)

            now = timezone.now()

            if professionnel.temp_code_verification and professionnel.temp_code_verification > now:

                remaining = professionnel.temp_code_verification - now
                minutes = remaining.seconds // 60
                seconds = remaining.seconds % 60

                return Response({
                    "status": False,
                    "message": f"Vous ne pouvez pas demander un nouveau code pour le moment. Réessayez dans {minutes} min {seconds} sec."
                }, status=status.HTTP_400_BAD_REQUEST)

            compteur = professionnel.nombre_send_email

            otp = generate_otp()

            professionnel.code_verification = otp
            professionnel.nombre_send_email += 1

            if compteur >= 2:
                professionnel.temp_code_verification = now + timedelta(minutes=30)

            professionnel.save()

            send_register_notification_professionnel(
                email=professionnel.email,
                nom_entreprise=professionnel.nom_entreprise,
                otp=otp
            )

            return Response({
                "status": True,
                "message": "Code envoyé avec succès.",
                "nombre_envoi": professionnel.nombre_send_email
            }, status=status.HTTP_200_OK)

        except Exception as e:

            logger.error("Erreur ProfessionnelResendOTPView : %s", str(e))

            return Response({
                "status": False,
                "message": "Une erreur interne est survenue."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)