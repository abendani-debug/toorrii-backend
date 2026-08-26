from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny
from adminToorrii.models import Service
from client.serializers import ServicePublicSerializer


class AfficherServicesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Client-Services"],
        summary="Lister les services actifs (public)",

        description=(
            "Retourne la liste des services actifs avec uniquement les champs publics.\n\n"
            "Optimisé pour performance (requête légère + tri + sélection de champs)."
        ),

        responses={
            200: OpenApiResponse(
                response=ServicePublicSerializer(many=True),
                description="Liste des services récupérée avec succès"
            ),
            500: OpenApiResponse(
                description="Erreur serveur interne"
            ),
        }
    )
    def get(self, request):

        try:
            #  requête optimisée
            services = (
                Service.objects
                .filter(actif=True)
                .only(
                    "nom_service",
                    "description_service",
                    "prix_service",
                    "duree_moyenne_creneau",
                    "type_reservation",
                    "actif",
                    "date_creation",
                    "photo_principal"
                )
                .order_by("-date_creation")
            )

            serializer = ServicePublicSerializer(services, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"message": "Erreur serveur interne"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )