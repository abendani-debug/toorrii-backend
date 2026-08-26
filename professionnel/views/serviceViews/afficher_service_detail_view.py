from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)

from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import (
    Service,
    ServicePlanning
)
from professionnel.serializers import ServiceDetailSerializer


class AfficherServiceDetailView(APIView):
    """
    GET - Détail d'un service du professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Services - Professionnel"],
        summary="Détail d'un service",
        description=(
            "Retourne un service spécifique appartenant au professionnel connecté.\n\n"
            "Inclut :\n"
            "- Planning complet\n"
            "- Pauses\n"
            "- Exceptions\n\n"
            " Sécurisé par authentification professionnel"
        ),
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du service à récupérer"
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Service récupéré avec succès",
                response=ServiceDetailSerializer,
                examples=[
                    OpenApiExample(
                        "Success response",
                        value={
                            "message": "Service récupéré avec succès",
                            "data": {
                                "service_id": "SRV_1",
                                "categorie": "CAT_1",
                                "nom_service": "Massage Relaxant",
                                "description_service": "Service de détente musculaire",
                                "prix_service": 2500,
                                "duree_moyenne_creneau": 30,
                                "actif": True,
                                "photo_principal": "/media/service.jpg",
                                "type_reservation": "FR",
                                "planning": [
                                    {
                                        "nom_jour": "LUNDI",
                                        "heure_debut_service": "08:00:00",
                                        "heure_fin_service": "16:00:00",
                                        "pauses": [
                                            {
                                                "pause_id": "PLNP_1",
                                                "description": "Pause déjeuner",
                                                "heure_debut_pause": "12:00:00",
                                                "heure_fin_pause": "13:00:00"
                                            }
                                        ]
                                    }
                                ],
                                "exceptions": [
                                    {
                                        "exception_id": "PLNE_1",
                                        "raison": "Formation",
                                        "raison_autre": None,
                                        "date_debut_exception": "2026-02-20",
                                        "date_fin_exception": "2026-02-20",
                                        "heure_debut_exception": "09:00:00",
                                        "heure_fin_exception": "17:00:00"
                                    }
                                ]
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Service introuvable",
                examples=[
                    OpenApiExample(
                        "Not found",
                        value={"message": "Service introuvable"}
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Forbidden",
                        value={
                            "detail": "Vous n'avez pas la permission d'effectuer cette action."
                        }
                    )
                ]
            ),
        }
    )
    def get(self, request, service_id):
        try:
            # -----------------------------
            # 1. Professionnel connecté
            # -----------------------------
            professionnel = request.user.professionnel_profile

            # -----------------------------
            # 2. Query optimisée ( performance + sécurité)
            # -----------------------------
            service = Service.objects.filter(
                service_id=service_id,
                professionnel=professionnel
            ).prefetch_related(
                Prefetch(
                    "planning",
                    queryset=ServicePlanning.objects.prefetch_related("pauses")
                ),
                "planning_exception"
            ).first()

            # -----------------------------
            # 3. Not found
            # -----------------------------
            if not service:
                return Response(
                    {"message": "Service introuvable"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # -----------------------------
            # 4. Serialization
            # -----------------------------
            serializer = ServiceDetailSerializer(
                service,
                context={"request": request}
            )

            return Response(
                {
                    "message": "Service récupéré avec succès",
                    "data": serializer.data
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