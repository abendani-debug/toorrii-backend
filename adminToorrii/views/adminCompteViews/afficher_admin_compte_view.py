from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import AdminAccountAfficherSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class AfficherAdminCompteView(APIView):
    """
    Endpoint pour afficher les informations du compte Admin lié à l'utilisateur connecté.
    Authentification JWT obligatoire.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Admin compte"],
        summary="Lire les informations du compte Admin",
        description="Retourne les informations détaillées du compte administrateur lié à l'utilisateur actuellement connecté.",
        responses={
            200: OpenApiResponse(
                response=AdminAccountAfficherSerializer,
                description="Informations récupérées avec succès",
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "nom": "Admin Exemple",
                            "email": "admin@example.com",
                            "numero_telephone": "+213660000000",
                            "niveau_acces": "Super_A",
                            "est_super_admin": True,
                            "etat_compte": "A",
                            "date_creation": "2025-12-20T13:00:00Z"
                        }
                    )
                ]
            ),
            401: OpenApiResponse(
                description="Non authentifié ou JWT invalide",
                examples=[
                    OpenApiExample(
                        "Réponse 401",
                        value={"detail": "Authentication credentials were not provided."}
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={"detail": "Vous n'avez pas la permission d'accéder à cette ressource."}
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Profil Admin lié introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"error": "Profil Admin introuvable pour cet utilisateur."}
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur serveur interne",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={"error": "Une erreur interne est survenue."}
                    )
                ]
            )
        }
    )
    def get(self, request):
        try:
            # Récupère le profil admin lié à l'utilisateur
            admin_user = getattr(request.user, "admin_profile", None)
            if not admin_user:
                return Response(
                    {"error": "Profil Admin introuvable pour cet utilisateur."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = AdminAccountAfficherSerializer(admin_user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Erreur dans AfficherAdminCompteView: %s", str(e))
            return Response(
                {"error": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )