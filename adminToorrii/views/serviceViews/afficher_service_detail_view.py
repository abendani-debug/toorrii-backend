from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from adminToorrii.models import Service
from adminToorrii.serializers import ServiceDetailSerializer
import logging

logger = logging.getLogger(__name__)

JOURS_SEMAINE = ['DIMANCHE', 'LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI']


class AfficherServiceDetailView(APIView):
    """
    GET /api/admin/services/<service_id>/
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Service"],
        summary="Afficher le détail complet d’un service",
        description=(
            "Retourne les informations complètes d’un service incluant :\n"
            "- Informations générales\n"
            "- Planning avec pauses\n"
            "- Exceptions\n"
            "- Jours de repos (calculés automatiquement)"
        ),
        responses={
            200: OpenApiResponse(
                description="Détails du service",
                examples=[
                    OpenApiExample(
                        "Réponse complète",
                        value={
                            "status": True,
                            "data": {
                                "service": {},
                                "planning": [],
                                "exceptions": [],
                                "jours_repos": ["DIMANCHE"]
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(description="Service introuvable"),
            500: OpenApiResponse(description="Erreur serveur")
        }
    )
    def get(self, request, service_id):
        try:
            #  Optimisation DB (TRÈS IMPORTANT)
            service = Service.objects.prefetch_related(
                "planning__pauses",
                "planning_exception"
            ).get(pk=service_id)

            #  Serializer principal
            serializer = ServiceDetailSerializer(service)

            # =========================
            # Planning + jours travail
            # =========================
            planning_list = []
            jours_travail = []

            for planning in service.planning.all():
                pauses_list = [
                    {
                        "pause_id": pause.service_planning_pause_id,
                        "description": pause.description,
                        "heure_debut_pause": pause.heure_debut_pause,
                        "heure_fin_pause": pause.heure_fin_pause,
                    }
                    for pause in planning.pauses.all()
                ]

                planning_list.append({
                    "service_planning_id": planning.service_planning_id,
                    "nom_jour": planning.nom_jour,
                    "heure_debut_service": planning.heure_debut_service,
                    "heure_fin_service": planning.heure_fin_service,
                    "pauses": pauses_list
                })

                jours_travail.append(planning.nom_jour)

            # =========================
            # Exceptions
            # =========================
            exceptions_list = [
                {
                    "exception_id": exc.service_planning_exception_id,
                    "raison": exc.raison,
                    "raison_autre": exc.raison_autre,
                    "date_debut_exception": exc.date_debut_exception,
                    "date_fin_exception": exc.date_fin_exception,
                    "heure_debut_exception": exc.heure_debut_exception,
                    "heure_fin_exception": exc.heure_fin_exception,
                }
                for exc in service.planning_exception.all()
            ]

            # =========================
            # Jours repos
            # =========================
            jours_repos = [j for j in JOURS_SEMAINE if j not in jours_travail]

            # =========================
            # RESPONSE
            # =========================
            return Response(
                {
                    "status": True,
                    "data": {
                        "service": serializer.data,
                        "planning": planning_list,
                        "exceptions": exceptions_list,
                        "jours_repos": jours_repos
                    }
                },
                status=status.HTTP_200_OK
            )

        except Service.DoesNotExist:
            return Response(
                {"status": False, "message": "Service introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error("Erreur AfficherServiceDetailView: %s", str(e))
            return Response(
                {"status": False, "message": "Erreur interne serveur"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )