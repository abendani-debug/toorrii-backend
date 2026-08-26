from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Professionnel
from adminToorrii.serializers import ProfessionnelSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)


class ModifierProfessionnelView(APIView):
    """
    PUT /api/admin/professionnels/<professionnel_id>/
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Professionnels"],
        summary="Modifier un professionnel",
        description="Met à jour les informations d’un professionnel.",
        request=ProfessionnelSerializer,
        responses={
            200: OpenApiResponse(
                description="Professionnel modifié avec succès",
                response=ProfessionnelSerializer,
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "message": "Professionnel modifié avec succès.",
                            "data": {
                                "professionnel_id": "PRO_1",
                                "nom_entreprise": "ENTREPRISE MARTIN",
                                "email": "contact@martin.com",
                                "numero_telephone": "+213600000000",
                                "adresse": "Oran",
                                "wilaya": "Oran",
                                "description": "Consultante marketing",
                                "etat_compte": "A",
                                "date_creation": "2025-12-18T10:10:00Z"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Données invalides"),
            404: OpenApiResponse(description="Professionnel introuvable"),
            500: OpenApiResponse(description="Erreur serveur"),
        }
    )
    def put(self, request, professionnel_id):
        try:
            # -------------------------
            # GET PROFESSIONNEL
            # -------------------------
            try:
                pro = Professionnel.objects.get(professionnel_id=professionnel_id)
            except Professionnel.DoesNotExist:
                return Response(
                    {"status": False, "message": "Professionnel introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # -------------------------
            # SERIALIZER UPDATE
            # -------------------------
            serializer = ProfessionnelSerializer(
                pro,
                data=request.data,
                partial=True,
                context={"request": request}
            )

            if not serializer.is_valid():
                return Response(
                    {"status": False, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            professionnel = serializer.save()

            return Response(
                {
                    "status": True,
                    "message": "Professionnel modifié avec succès.",
                    "data": ProfessionnelSerializer(professionnel).data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Erreur ModifierProfessionnelView: %s", str(e))
            return Response(
                {
                    "status": False,
                    "error": "Une erreur interne est survenue."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )