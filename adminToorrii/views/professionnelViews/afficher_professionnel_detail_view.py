from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Professionnel
from adminToorrii.serializers import ProfessionnelSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class ProfessionnelDetailView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Professionnels"],
        summary="Afficher les détails d’un professionnel",
        description="Récupère les détails complets d’un professionnel identifié par `professionnel_id`.",
        responses={
            200: OpenApiResponse(
                description="Professionnel récupéré avec succès",
                response=ProfessionnelSerializer,
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "data": {
                                "professionnel_id": "pro_1",
                                "nom_entreprise": "Entreprise Dupont",
                                "email": "contact@dupont.com",
                                "numero_telephone": "+33123456789",
                                "adresse": "123 Rue Principale",
                                "wilaya": ["Paris"],
                                "description": "Expert en informatique",
                                "logo": "/media/assets/partenaire_logos/logo.png",
                                "code_qr": "/media/assets/partenaire_code_qr/pro_1.png",
                                "siteweb": "https://dupont.com",
                                "facebook": "",
                                "tiktok": "",
                                "instagram": "",
                                "etat_compte": "A",
                                "compte_verification": False,
                                "confirmation_rdv_auto": True,
                                "theme_couleur": "bleu",
                                "date_inscription": "2025-12-18T10:00:00Z",
                                "date_creation": "2025-12-18T10:00:00Z"
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Professionnel introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Professionnel non trouvé."}
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={"status": False, "error": "Une erreur interne est survenue."}
                    )
                ]
            ),
        }
    )
    def get(self, request, professionnel_id):
        try:
            try:
                pro = Professionnel.objects.get(professionnel_id=professionnel_id)
            except Professionnel.DoesNotExist:
                return Response(
                    {"status": False, "message": "Professionnel non trouvé."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = ProfessionnelSerializer(pro)
            return Response(
                {"status": True, "data": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Erreur dans ProfessionnelDetailView: %s", str(e))
            return Response(
                {"status": False, "error": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
