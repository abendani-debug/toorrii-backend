from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsProfessionnelUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from adminToorrii.models import Professionnel
from professionnel.serializers import ProfessionnelSerializer

class ProfessionnelDetailCompteView(APIView):
    """
    Endpoint pour récupérer les détails du professionnel connecté.
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel"],
        summary="Détails du professionnel connecté",
        description=(
            "Récupère les informations complètes du professionnel connecté.\n\n"
            "Sécurité :\n"
            "- Requiert un access token JWT valide."
        ),
        responses={
            200: OpenApiResponse(
                response=ProfessionnelSerializer,
                description="Détails récupérés avec succès",
                examples=[
                    OpenApiExample(
                        "Exemple succès",
                        summary="Détails du professionnel",
                        value={
                            "professionnel_id": "pro_1",
                            "nom_entreprise": "SERVICUP",
                            "email": "pro@test.com",
                            "numero_telephone": "+213661234567",
                            "adresse": "Alger",
                            "wilaya": ["Alger"],
                            "description": "Entreprise de services",
                            "etat_compte": "A",
                            "logo": "/media/professionnel/professionnel_logos/logo.png",
                            "code_qr": "/media/professionnel/professionnel_code_qr/qr_pro_1.png",
                            "compte_verification": True,
                            "confirmation_rdv_auto": True,
                            "theme_couleur": "bleu",
                            "date_inscription": "2026-04-09T00:00:00Z",
                            "nombre_sms": 10,
                            "nombre_priorite": 1,
                            "siteweb": "https://monentreprise.com",
                            "facebook": "https://facebook.com/monentreprise",
                            "instagram": "https://instagram.com/monentreprise",
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description="Non authentifié"),
            404: OpenApiResponse(description="Profil professionnel introuvable"),
        }
    )
    def get(self, request):
        utilisateur = request.user
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProfessionnelSerializer(professionnel)
        return Response(serializer.data, status=status.HTTP_200_OK)