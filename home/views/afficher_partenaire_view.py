from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

from adminToorrii.models import Partenaire
from adminToorrii.serializers import PartenaireAdminSerializer, PartenairePublicSerializer

logger = logging.getLogger(__name__)

class AfficherPartenaireView(APIView):
    """
    Endpoint pour afficher la liste des partenaires.
    Accessible par tous les utilisateurs.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Afficher la liste des partenaires",
        description="Endpoint pour afficher la liste complète des partenaires.",
        responses={
            200: OpenApiResponse(
                description="Liste des partenaires récupérée avec succès",
                response=PartenaireAdminSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Réponse 200 Admin",
                        value={
                            "message": "Liste des partenaires récupérée avec succès",
                            "data": [
                                {
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
                            ]
                        }
                    ),
                    OpenApiExample(
                        "Réponse 200 Public",
                        value={
                            "message": "Liste des partenaires récupérée avec succès",
                            "data": [
                                {
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
                            ]
                        }
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
    def get(self, request):
        try:
            if request.user.is_authenticated:
                # Admin view → toutes les données
                partenaires = Partenaire.objects.all().order_by('-priorite_affichage', '-date_ajout')
                serializer = PartenaireAdminSerializer(partenaires, many=True)
            else:
                # Public view → seulement partenaires actifs
                partenaires = Partenaire.objects.filter(actif=True).order_by('-priorite_affichage', '-date_ajout')
                serializer = PartenairePublicSerializer(partenaires, many=True)

            return Response(
                {"status": True, "message": "Liste des partenaires récupérée avec succès", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("Erreur dans AfficherPartenaireView: %s", str(e))
            return Response(
                {"status": False, "message": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
