from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import PolitiqueConfidentialite
from adminToorrii.serializers import PolitiqueConfidentialiteAdminSerializer as PolitiqueConfidentialiteSerializer
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class AjouterPolitiqueView(APIView):
    """
    POST /api/politique/ajouter/
    Endpoint pour créer une nouvelle politique de confidentialité.
    Seuls les admins actifs peuvent ajouter.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Politique de confidentialité"],
        summary="Ajouter une nouvelle politique (Admin actif uniquement)",
        description=(
            "Crée une nouvelle politique de confidentialité.\n\n"
            "⚠ Une seule politique peut être active à la fois. "
            "Si la nouvelle est active, l'ancienne sera désactivée automatiquement.\n\n"
            "Seuls les administrateurs actifs (`etat_compte='A'`) peuvent effectuer cette action.\n"
            "La version de la politique doit être unique."
        ),
        request=PolitiqueConfidentialiteSerializer,
        responses={
            201: OpenApiResponse(
                description="Politique ajoutée avec succès",
                response=PolitiqueConfidentialiteSerializer(many=False),
                examples=[
                    OpenApiExample(
                        "Réponse 201",
                        value={
                            "status": True,
                            "message": "Politique ajoutée avec succès",
                            "data": {
                                "politique_id": "POL_2",
                                "titre": {"fr": "Politique de confidentialité", "en": "Privacy Policy", "ar": "سياسة الخصوصية"},
                                "contenu": {"fr": "Contenu FR", "en": "Content EN", "ar": "المحتوى AR"},
                                "version": 2,
                                "active": True,
                                "date_creation": "2025-12-20T15:00:00Z",
                                "historique_modifications": ["Créé le 2025-12-20 15:00:00"]
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Données invalides",
                examples=[
                    OpenApiExample(
                        "Réponse 400",
                        value={
                            "status": False,
                            "message": "Données invalides",
                            "details": {
                                "version": ["Cette version existe déjà."],
                                "titre": ["Clé 'en' manquante."]
                            }
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Compte admin inactif ou accès refusé",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={"status": False, "message": "Compte admin inactif. Action non autorisée."}
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
    def post(self, request):
        try:

            serializer = PolitiqueConfidentialiteSerializer(data=request.data)
            if serializer.is_valid():
                #  Si la nouvelle politique est active, désactiver l'ancienne
                if serializer.validated_data.get('active', False):
                    PolitiqueConfidentialite.objects.filter(active=True).update(active=False)

                serializer.save()

                return Response(
                    {"status": True, "message": "Politique ajoutée avec succès", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {"status": False, "message": "Données invalides", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error("Erreur dans AjouterPolitiqueView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )