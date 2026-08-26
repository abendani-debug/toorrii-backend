from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny
from adminToorrii.models import Categorie
from client.serializers import CategorieAfficherSerializer


class ListeCategoriesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Client-Catégories"],
        summary="Lister toutes les catégories actives",

        description=(
            "Retourne la liste des catégories actives triées par ordre d'affichage.\n\n"
            "Les données multilingues sont retournées en JSON (nom + description)."
        ),

        responses={
            200: OpenApiResponse(
                response=CategorieAfficherSerializer(many=True),
                description="Liste des catégories récupérée avec succès"
            ),
            404: OpenApiResponse(description="Aucune catégorie trouvé"),
            500: OpenApiResponse(description="Erreur serveur interne"),
        }
    )
    def get(self, request):

        categories = Categorie.objects.filter(
            active=True,
            parent__isnull=True
        ).order_by("ordre_affichage")

        serializer = CategorieAfficherSerializer(categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)