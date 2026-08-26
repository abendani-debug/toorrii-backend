from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Professionnel
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
import logging

logger = logging.getLogger(__name__)

class SupprimerProfessionnelView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Professionnels"],
        summary="Supprimer un professionnel",
        description="Supprime définitivement un professionnel identifié par `professionnel_id`.",
        responses={
            200: OpenApiResponse(
                description="Professionnel supprimé avec succès",
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "message": "Professionnel supprimé définitivement."
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Professionnel introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "Professionnel introuvable."}
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={"status": False, "error": "Une erreur interne est survenue."}
                    )
                ]
            ),
        }
    )
    def delete(self, request, professionnel_id):
        try:
            try:
                pro = Professionnel.objects.get(professionnel_id=professionnel_id)
            except Professionnel.DoesNotExist:
                return Response(
                    {"status": False, "message": "Professionnel introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            pro.delete()
            return Response(
                {"status": True, "message": "Professionnel supprimé définitivement."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Erreur dans SupprimerProfessionnelView: %s", str(e))
            return Response(
                {"status": False, "error": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
