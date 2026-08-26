from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.permissions import AllowAny
from adminToorrii.models import Service, Professionnel
from client.serializers import ServicePublicSerializer


class AfficherServicesParProfessionnelView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Client-Services"],
        summary="Lister les services par professionnel",

        description=(
            "Retourne la liste des services actifs d’un professionnel.\n\n"
            "Le professionnel est identifié par son ID."
        ),

        parameters=[
            OpenApiParameter(
                name="professionnel_id",
                description="ID du professionnel (ex: pro_1)",
                required=True,
                type=str,
                location=OpenApiParameter.PATH
            )
        ],

        responses={
            200: OpenApiResponse(
                response=ServicePublicSerializer(many=True),
                description="Liste des services récupérée avec succès"
            ),
            404: OpenApiResponse(description="Professionnel introuvable"),
            500: OpenApiResponse(description="Erreur serveur interne"),
        }
    )
    def get(self, request, professionnel_id):

        try:
            #  vérifier professionnel
            professionnel = Professionnel.objects.filter(
                professionnel_id=professionnel_id,
                etat_compte=Professionnel.EtatCompte.ACTIVE
            ).first()

            if not professionnel:
                return Response(
                    {"message": "Professionnel introuvable ou inactif"},
                    status=status.HTTP_404_NOT_FOUND
                )

            #  services filtrés + optimisés
            services = (
                Service.objects
                .filter(
                    professionnel=professionnel,
                    actif=True
                )
                .only(
                    "service_id",
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