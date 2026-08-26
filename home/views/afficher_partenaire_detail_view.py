from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

from adminToorrii.models import Partenaire
from adminToorrii.serializers import PartenaireAdminSerializer, PartenairePublicSerializer

logger = logging.getLogger(__name__)

class AfficherPartenaireDetailView(APIView):
    """
    Endpoint pour afficher un partenaire par ID.
    Accessible par tous les utilisateurs.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Afficher un partenaire par son ID",
        description="Récupère les détails d'un partenaire spécifique selon son partenaire_id.",
        parameters=[
            OpenApiExample(
                name="ID Partenaire",
                value={"partenaire_id": "PART1"},
                description="ID du partenaire à récupérer"
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Partenaire récupéré avec succès",
                response=PartenaireAdminSerializer(many=False),
                examples=[
                    OpenApiExample(
                        "Réponse 200 Admin",
                        value={
                            "status": True,
                            "message": "Partenaire récupéré avec succès",
                            "data": {
                                "partenaire_id": "PART1",
                                "nom_partenaire": {"fr": "Société A", "en": "Company A", "ar": "شركة أ"},
                                "logo": "http://domain.com/media/partenaire/partenaire_logos/logoA.png",
                                "description": {"fr": "Description FR", "en": "Description EN", "ar": "الوصف"},
                                "adresse": {"ville": "Alger", "rue": "Rue 1"},
                                "email": "contact@companya.com",
                                "telephone": "+213661234567",
                                "type_partenaire": ["COMMERCIAL"],
                                "site_web": "http://companya.com",
                                "image_banniere": "http://domain.com/media/partenaire/partenaire_banniere/bannerA.png",
                                "priorite_affichage": 1,
                                "date_deb": "2025-01-01T00:00:00Z",
                                "date_fin": "2025-12-31T23:59:59Z",
                                "actif": True,
                                "facebook": "http://facebook.com/companya",
                                "instagram": "http://instagram.com/companya",
                                "tiktok": "http://tiktok.com/@companya",
                                "liens_externes": ["http://example.com"],
                                "date_creation_entreprise": "2020-01-01"
                            }
                        }
                    ),
                    OpenApiExample(
                        "Réponse 200 Public",
                        value={
                            "status": True,
                            "message": "Partenaire récupéré avec succès",
                            "data": {
                                "nom_partenaire": {"fr": "Société A", "en": "Company A", "ar": "شركة أ"},
                                "logo": "http://domain.com/media/partenaire/partenaire_logos/logoA.png",
                                "description": {"fr": "Description FR", "en": "Description EN", "ar": "الوصف"},
                                "adresse": {"ville": "Alger", "rue": "Rue 1"},
                                "email": "contact@companya.com",
                                "telephone": "+213661234567",
                                "type_partenaire": ["COMMERCIAL"],
                                "site_web": "http://companya.com",
                                "image_banniere": "http://domain.com/media/partenaire/partenaire_banniere/bannerA.png"
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Partenaire introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Aucun partenaire trouvé avec l'ID PART1"}
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
            )
        }
    )
    def get(self, request, partenaire_id):
        try:
            partenaire = Partenaire.objects.get(partenaire_id=partenaire_id)

            serializer = (
                PartenaireAdminSerializer(partenaire)
                if request.user.is_authenticated
                else PartenairePublicSerializer(partenaire)
            )

            return Response(
                {"status": True, "message": "Partenaire récupéré avec succès", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Partenaire.DoesNotExist:
            return Response(
                {"status": False, "message": f"Aucun partenaire trouvé avec l'ID {partenaire_id}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error("Erreur dans AfficherPartenaireDetailView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
