from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import Partenaire
from adminToorrii.serializers import PartenaireAdminSerializer as PartenaireSerializer
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

class ModifierPartenaireView(APIView):
    """
    Endpoint pour modifier un partenaire existant.
    Seuls les admins actifs peuvent modifier un partenaire.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Partenaire"],
        summary="Modifier un partenaire",
        description=(
            "Permet à un administrateur connecté de modifier les informations d'un partenaire existant. "
            "Les champs JSON comme `nom_partenaire` et `description` doivent contenir les clés obligatoires : 'fr', 'en', 'ar'."
        ),
        request=PartenaireSerializer,
        responses={
            200: OpenApiResponse(
                description="Partenaire modifié avec succès",
                response=PartenaireSerializer
            ),
            400: OpenApiResponse(
                description="Données invalides",
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
            403: OpenApiResponse(description="Accès refusé pour les utilisateurs non-admin"),
            404: OpenApiResponse(description="Partenaire introuvable")
        },
        examples=[
            OpenApiExample(
                "Exemple de modification",
                value={
                    "nom_partenaire": {"fr": "Partenaire FR Modifié", "en": "Partner EN Updated", "ar": "شريك AR محدث"},
                    "logo": "path/to/new_logo.png",
                    "description": {"fr": "Nouvelle description FR", "en": "New description EN", "ar": "وصف جديد AR"},
                    "adresse": {"fr": "Nouvelle adresse FR", "en": "New address EN", "ar": "عنوان جديد AR"},
                    "site_web": "https://www.nouveau-site.com",
                    "actif": True,
                    "type_partenaire": ["COMMERCIAL"],
                    "date_deb": "2025-01-01T00:00:00Z",
                    "date_fin": "2025-12-31T23:59:59Z"
                }
            )
        ]
    )
    def put(self, request, partenaire_id):
        try:
            partenaire = Partenaire.objects.get(partenaire_id=partenaire_id)
        except Partenaire.DoesNotExist:
            return Response(
                {"error": f"Aucun partenaire trouvé avec l'id {partenaire_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PartenaireSerializer(
            partenaire, data=request.data, partial=True  # partial=True permet modification partielle
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Partenaire modifié avec succès", "data": serializer.data},
            status=status.HTTP_200_OK
        )
