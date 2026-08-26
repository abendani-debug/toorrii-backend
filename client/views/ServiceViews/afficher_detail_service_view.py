from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny
from adminToorrii.models import Service
from client.serializers import ServiceDetailSerializer


class AfficherDetailServiceView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Client-Services"],
        summary="Détail d’un service complet",

        description=(
            "Retourne toutes les informations d’un service :\n"
            "- infos service\n"
            "- planning (jours + horaires)\n"
            "- pauses\n"
            "- exceptions"
        ),

        responses={
            200: OpenApiResponse(
                response=ServiceDetailSerializer,
                description="Détail du service récupéré avec succès"
            ),
            404: OpenApiResponse(description="Service introuvable"),
            500: OpenApiResponse(description="Erreur serveur interne"),
        }
    )
    def get(self, request, service_id):

        try:
            service = Service.objects.filter(
                service_id=service_id,
                actif=True
            ).prefetch_related(
                "planning__pauses",
                "planning_exception"
            ).first()

            if not service:
                return Response(
                    {"message": "Service introuvable"},
                    status=status.HTTP_404_NOT_FOUND
                )

            #  BUILD DATA MANUEL (OPTIMISÉ + CONTRÔLÉ)

            planning_data = []
            for p in service.planning.all():
                planning_data.append({
                    "nom_jour": p.nom_jour,
                    "heure_debut_service": p.heure_debut_service,
                    "heure_fin_service": p.heure_fin_service,
                    "pauses": [
                        {
                            "description": pause.description,
                            "heure_debut_pause": pause.heure_debut_pause,
                            "heure_fin_pause": pause.heure_fin_pause,
                        }
                        for pause in p.pauses.all()
                    ]
                })

            exception_data = []
            for e in service.planning_exception.all():
                exception_data.append({
                    "raison": e.raison,
                    "raison_autre": e.raison_autre,
                    "date_debut_exception": e.date_debut_exception,
                    "date_fin_exception": e.date_fin_exception,
                    "heure_debut_exception": e.heure_debut_exception,
                    "heure_fin_exception": e.heure_fin_exception,
                })

            data = {
                "service_id": service.service_id,
                "nom_service": service.nom_service,
                "description_service": service.description_service,
                "prix_service": service.prix_service,
                "duree_moyenne_creneau": service.duree_moyenne_creneau,
                "type_reservation": service.type_reservation,
                "actif": service.actif,
                "date_creation": service.date_creation,
                "photo_principal": (
                    request.build_absolute_uri(service.photo_principal.url)
                    if service.photo_principal else None
                ),

                "planning": planning_data,
                "planning_exception": exception_data
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"message": "Erreur serveur interne"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )