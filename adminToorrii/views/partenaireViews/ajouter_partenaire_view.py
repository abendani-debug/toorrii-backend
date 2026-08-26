from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import Partenaire
from adminToorrii.serializers import PartenaireAdminSerializer as PartenaireSerializer
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

class AjouterPartenaireView(APIView):
    """
    Endpoint pour ajouter un partenaire.
    Seuls les admins actifs peuvent ajouter un partenaire.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Partenaire"],
        summary="Ajouter un partenaire",
        description=(
            "Permet à un administrateur connecté de créer un nouveau partenaire. "
            "Les champs `nom_partenaire` et `description` doivent contenir les clés obligatoires : 'fr', 'en', 'ar'. "
            "La priorité d'affichage est gérée automatiquement si non fournie."
        ),
        request=PartenaireSerializer,
        responses={
            201: OpenApiResponse(
                description="Partenaire créé avec succès",
                response=PartenaireSerializer
            ),
            400: OpenApiResponse(
                description="Données invalides ou validation échouée",
                examples=[
                    OpenApiExample(
                        "Erreur validation",
                        value={
                            "error": "Données invalides",
                            "details": {
                                "nom_partenaire": ["Le champ 'nom_partenaire' doit contenir les clés obligatoires : fr, en, ar"]
                            }
                        }
                    )
                ]
            ),
            403: OpenApiResponse(description="Accès refusé pour les non-admins"),
            500: OpenApiResponse(description="Erreur serveur")
        },
        examples=[
            OpenApiExample(
                "Exemple de requête",
                value={
                    "nom_partenaire": {"fr": "Partenaire FR", "en": "Partner EN", "ar": "شريك AR"},
                    "logo": "path/to/logo.png",
                    "description": {"fr": "Description FR", "en": "Description EN", "ar": "الوصف AR"},
                    "adresse": {"fr": "Adresse FR", "en": "Address EN", "ar": "العنوان AR"},
                    "email": "partenaire@example.com",
                    "telephone": "+213660000001",
                    "site_web": "https://www.partenaire.com",
                    "actif": True,
                    "type_partenaire": ["COMMERCIAL", "MARKETING"],
                    "date_deb": "2025-01-01T00:00:00Z",
                    "date_fin": "2025-12-31T23:59:59Z",
                    "liens_externes": ["https://www.facebook.com/partenaire"],
                    "date_creation_entreprise": "2020-01-01",
                    "image_banniere": "path/to/banner.png"
                }
            )
        ]
    )
    def post(self, request):
        try:
            serializer = PartenaireSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data.copy()

            nom_partenaire = validated_data.pop("nom_partenaire")
            email = validated_data.pop("email")
            telephone = validated_data.pop("telephone")

            # Création via le manager personnalisé
            partenaire = Partenaire.objects.create(
                nom_partenaire=nom_partenaire,
                email=email,
                telephone=telephone,
                **validated_data
            )

            response_serializer = PartenaireSerializer(partenaire)
            return Response(
                {"message": "Partenaire créé avec succès", "data": response_serializer.data},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": "Erreur serveur", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
