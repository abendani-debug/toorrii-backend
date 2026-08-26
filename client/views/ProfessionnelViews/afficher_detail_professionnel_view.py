from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.permissions import AllowAny
from adminToorrii.models import Professionnel
from client.serializers import ProfessionnelFullSerializer


class AfficherDetailProfessionnelView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Client-Professionnels"],
        summary="Afficher le détail d’un professionnel",

        description=(
            "Retourne toutes les informations d’un professionnel via son ID.\n\n"
            "Conditions :\n"
            "- Le professionnel doit exister\n"
            "- Le compte doit être actif"
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
                response=ProfessionnelFullSerializer,
                description="Détails du professionnel récupérés avec succès"
            ),
            404: OpenApiResponse(
                description="Professionnel introuvable ou inactif"
            ),
            500: OpenApiResponse(
                description="Erreur serveur interne"
            ),
        }
    )
    def get(self, request, professionnel_id):

        professionnel = Professionnel.objects.filter(
            professionnel_id=professionnel_id,
            etat_compte=Professionnel.EtatCompte.ACTIVE
        ).first()

        if not professionnel:
            return Response(
                {"message": "Professionnel introuvable ou inactif"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProfessionnelFullSerializer(professionnel)

        return Response(serializer.data, status=status.HTTP_200_OK)