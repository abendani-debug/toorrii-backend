from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
import logging

from adminToorrii.models import Professionnel
from authentication.serializers import ProfessionnelCheckNomEntrepriseSerializer


logger = logging.getLogger(__name__)

from rest_framework.permissions import  AllowAny

class ProfessionnelCheckNomEntrepriseView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Authentification Professionnel"],
        summary="Vérifier l'existence d'un nom d'entreprise",
        description="""
Permet de vérifier si un **nom d'entreprise professionnel** existe déjà dans la base de données.

### Utilisation

Cet endpoint est utilisé pour :

- Vérifier la **disponibilité d'un nom d'entreprise**
- Empêcher les **doublons lors de l'inscription**
- Vérification côté **frontend en temps réel**

### Fonctionnement

1 Le client envoie `nom_entreprise`  
2 Le système recherche ce nom dans la base de données  
3 Le système retourne si ce nom existe ou non
""",
        request=ProfessionnelCheckNomEntrepriseSerializer,
        responses={
            200: OpenApiResponse(
                description="Résultat de la vérification",
                examples=[
                    OpenApiExample(
                        "Nom existant",
                        summary="Entreprise déjà enregistrée",
                        value={
                            "status": True,
                            "exists": True,
                            "message": "Un professionnel avec ce nom d'entreprise existe déjà."
                        }
                    ),
                    OpenApiExample(
                        "Nom disponible",
                        summary="Nom disponible",
                        value={
                            "status": True,
                            "exists": False,
                            "message": "Ce nom d'entreprise est disponible."
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur de validation",
                examples=[
                    OpenApiExample(
                        "Erreur validation",
                        value={
                            "status": False,
                            "errors": {
                                "nom_entreprise": [
                                    "Ce champ est obligatoire."
                                ]
                            }
                        }
                    )
                ]
            ),

            500: OpenApiResponse(
                description="Erreur interne serveur",
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
                    "nom_entreprise": "Clinique Santé DZ"
                }
            )
        ]
    )
    def post(self, request):

        try:

            serializer = ProfessionnelCheckNomEntrepriseSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    "status": False,
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            nom_entreprise = serializer.validated_data["nom_entreprise"].upper()

            exists = Professionnel.objects.filter(
                nom_entreprise__iexact=nom_entreprise
            ).exists()

            if exists:

                return Response({
                    "status": True,
                    "exists": True,
                    "message": "Un professionnel avec ce nom d'entreprise existe déjà."
                }, status=status.HTTP_200_OK)

            return Response({
                "status": True,
                "exists": False,
                "message": "Ce nom d'entreprise est disponible."
            }, status=status.HTTP_200_OK)

        except Exception as e:

            logger.error(
                "Erreur ProfessionnelCheckNomEntrepriseView : %s",
                str(e)
            )

            return Response({
                "status": False,
                "message": "Une erreur interne est survenue."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)