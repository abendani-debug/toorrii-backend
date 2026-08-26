from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import AboutNous
from adminToorrii.serializers import AboutNousAdminSerializer, AboutNousPublicSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class AfficherAboutNousDetailView(APIView):
    """
    Endpoint pour afficher les détails d`un enregistrement de la table aboutNous 
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Afficher une caractéristiques de l'entreprise",
        description="Retourne les detail d`un enregistrement de la table 'aboutNous'. Les utilisateurs authentifiés "
                    "reçoivent toutes les données, le public reçoit une version limitée.",
        responses={
            200: OpenApiResponse(
                description="récupérée avec succès",
                response=AboutNousAdminSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "message": "récupérée avec succès",
                            "data": [
                                {
                                    "about_id": "about1",
                                    "titre": {"fr": "À propos", "en": "About Us", "ar": "معلومات عنا"},
                                    "slogan": {"fr": "Excellence et Innovation", "en": "Excellence and Innovation", "ar": "التميز والابتكار"},
                                    "contenu": {"fr": "Contenu FR", "en": "Content EN", "ar": "المحتوى AR"},
                                    "mission": {"fr": "Notre mission FR", "en": "Our mission EN", "ar": "مهمتنا AR"},
                                    "vision": {"fr": "Notre vision FR", "en": "Our vision EN", "ar": "رؤيتنا AR"},
                                    "valeurs": {"fr": "Valeurs FR", "en": "Values EN", "ar": "قيمنا AR"},
                                    "pourquoi_choisir_nous": {"fr": "Pourquoi FR", "en": "Why EN", "ar": "لماذا AR"},
                                    "qui_nous_servons": {"fr": "Clients FR", "en": "Clients EN", "ar": "عملائنا AR"},
                                    "version": 1,
                                    "active": True,
                                    "date_creation": "2025-12-20T15:30:00Z",
                                    "historique_modifications": ["Modification le 2025-12-20T16:00:00"]
                                }
                            ]
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Aucune entrée trouvée",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Aucune entrée trouvée"}
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne du serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={"status": False, "message": "Une erreur interne est survenue."}
                    )
                ]
            ),
        }
    )
    def get(self, request, about_id):
        try:
            about_nous = AboutNous.objects.get(about_id=about_id)

            serializer = (
                AboutNousAdminSerializer(about_nous)
                if request.user.is_authenticated
                else AboutNousPublicSerializer(about_nous)
            )

            return Response(
                {"status": True, "message": "récupérée avec succès", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Erreur dans AfficherAboutNousView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
