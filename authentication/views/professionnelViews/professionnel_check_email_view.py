from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
import logging
from rest_framework.permissions import  AllowAny

from adminToorrii.models import Professionnel
from authentication.serializers import ProfessionnelCheckEmailSerializer


logger = logging.getLogger(__name__)


class ProfessionnelCheckEmailView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Authentification Professionnel"],
        summary="Vérifier l'existence d'un email professionnel",
        description="""
Permet de vérifier si un **compte professionnel existe** dans la base de données à partir de son **email**.

### Utilisation

Cet endpoint est généralement utilisé pour :

- Vérifier si un compte existe avant **connexion**
- Vérifier si un compte existe avant **réinitialisation du mot de passe**
- Vérifier si un email est **déjà enregistré**

### Fonctionnement

1 Le client envoie un email  
2 Le système recherche cet email dans la base  
3 Le système retourne si le compte existe ou non
""",
        request=ProfessionnelCheckEmailSerializer,
        responses={

            200: OpenApiResponse(
                description="Résultat de la vérification",
                examples=[
                    OpenApiExample(
                        "Email existant",
                        summary="Compte trouvé",
                        value={
                            "status": True,
                            "exists": True,
                            "message": "Un compte professionnel avec cet email existe."
                        }
                    ),
                    OpenApiExample(
                        "Email inexistant",
                        summary="Compte non trouvé",
                        value={
                            "status": True,
                            "exists": False,
                            "message": "Aucun compte professionnel avec cet email."
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation",
                examples=[
                    OpenApiExample(
                        "Email invalide",
                        value={
                            "status": False,
                            "errors": {
                                "email": ["Ce champ est obligatoire."]
                            }
                        }
                    )
                ]
            ),

            500: OpenApiResponse(
                description="Erreur interne du serveur",
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
                "Exemple requête",
                request_only=True,
                value={
                    "email": "contact@clinique-dz.com"
                }
            )
        ]
    )
    def post(self, request):

        try:

            serializer = ProfessionnelCheckEmailSerializer(data=request.data)

            if not serializer.is_valid():

                return Response({
                    "status": False,
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            email = serializer.validated_data["email"]

            exists = Professionnel.objects.filter(email=email).exists()

            if exists:

                return Response({
                    "status": True,
                    "exists": True,
                    "message": "Un compte professionnel avec cet email existe."
                }, status=status.HTTP_200_OK)

            return Response({
                "status": True,
                "exists": False,
                "message": "Aucun compte professionnel avec cet email."
            }, status=status.HTTP_200_OK)

        except Exception as e:

            logger.error("Erreur ProfessionnelCheckEmailView : %s", str(e))

            return Response({
                "status": False,
                "message": "Une erreur interne est survenue."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)