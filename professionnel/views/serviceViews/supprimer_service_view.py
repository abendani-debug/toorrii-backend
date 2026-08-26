from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample
)

from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import Service


class SupprimerServiceView(APIView):
    """
    DELETE - Supprimer un service (professionnel connecté)
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Services - Professionnel"],
        summary="Supprimer un service",
        description="""
        Supprime définitivement un service du professionnel connecté.

         Action irréversible :
        - Service supprimé
        - Planning supprimé (cascade)
        - Pauses supprimées (cascade)
        - Exceptions supprimées (cascade)
        """,
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du service"
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Service supprimé avec succès",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "message": "Service supprimé avec succès",
                            "service_id": "SER_1"
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Service introuvable",
                examples=[
                    OpenApiExample(
                        "Not found",
                        value={"message": "Service introuvable ou non autorisé"}
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Forbidden",
                        value={"message": "Utilisateur non professionnel"}
                    )
                ]
            ),
        }
    )
    def delete(self, request, service_id):
        try:
            # -------------------------
            # 1. PROFESSIONNEL CONNECTÉ
            # -------------------------
            try:
                professionnel = request.user.professionnel_profile
            except Exception:
                return Response(
                    {"message": "Utilisateur non professionnel"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # -------------------------
            # 2. RÉCUPÉRATION SÉCURISÉE
            # -------------------------
            service = Service.objects.filter(
                service_id=service_id,
                professionnel=professionnel
            ).first()

            if not service:
                return Response(
                    {"message": "Service introuvable ou non autorisé"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # -------------------------
            # 3. SUPPRESSION
            # -------------------------
            service.delete()

            # -------------------------
            # 4. RESPONSE
            # -------------------------
            return Response(
                {
                    "message": "Service supprimé avec succès",
                    "service_id": service_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "message": "Erreur interne serveur",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )