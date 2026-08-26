from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
import logging
from rest_framework.permissions import  AllowAny

from adminToorrii.models import Professionnel
from authentication.serializers import ProfessionnelVerifyOTPSerializer

logger = logging.getLogger(__name__)


class ProfessionnelVerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Authentification Professionnel"],
        summary="Vérification du code OTP",
        description="""
Permet de **vérifier le code OTP envoyé par email** lors de l'inscription du professionnel.

### Fonctionnement

Le professionnel doit fournir :

- son **email**
- le **code OTP reçu par email**

### Vérifications effectuées

1 Vérifier si le compte existe

2 Vérifier si le compte est déjà vérifié

3 Vérifier si le code OTP correspond

### Si le code est correct

Le système :

- active le compte (`compte_verification = True`)
- supprime le code OTP

### Sécurité

Le code OTP ne peut être utilisé **qu'une seule fois**.
""",
        request=ProfessionnelVerifyOTPSerializer,
        responses={
            200: OpenApiResponse(
                description="Compte vérifié avec succès",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "status": True,
                            "message": "Compte vérifié avec succès."
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Code OTP incorrect",
                examples=[
                    OpenApiExample(
                        "Code incorrect",
                        value={
                            "status": False,
                            "message": "Code de vérification incorrect."
                        }
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Compte non trouvé",
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

            409: OpenApiResponse(
                description="Compte déjà vérifié",
                examples=[
                    OpenApiExample(
                        "Compte déjà vérifié",
                        value={
                            "status": False,
                            "message": "Ce compte est déjà vérifié."
                        }
                    )
                ]
            ),

            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        "Erreur interne",
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
                request_only=True,
                value={
                    "email": "contact@clinique-dz.com",
                    "code_verification": "458921"
                }
            )
        ]
    )
    def post(self, request):

        try:

            serializer = ProfessionnelVerifyOTPSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data["email"]
            code = serializer.validated_data["code_verification"]

            try:
                professionnel = Professionnel.objects.get(email=email)
            except Professionnel.DoesNotExist:

                return Response({
                    "status": False,
                    "message": "Aucun compte professionnel avec cet email."
                }, status=status.HTTP_404_NOT_FOUND)

            if professionnel.compte_verification:

                return Response({
                    "status": False,
                    "message": "Ce compte est déjà vérifié."
                }, status=status.HTTP_409_CONFLICT)

            if professionnel.code_verification != code:

                return Response({
                    "status": False,
                    "message": "Code de vérification incorrect."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Activation du compte
            professionnel.compte_verification = True
            professionnel.etat_compte = 'A'

            # Nettoyage OTP
            professionnel.code_verification = None
            professionnel.temp_code_verification = None
            professionnel.nombre_send_email = 0

            professionnel.save()

            return Response({
                "status": True,
                "message": "Compte vérifié avec succès."
            }, status=status.HTTP_200_OK)

        except Exception as e:

            logger.error("Erreur ProfessionnelVerifyOTPView : %s", str(e))

            return Response({
                "status": False,
                "message": "Une erreur interne est survenue."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)