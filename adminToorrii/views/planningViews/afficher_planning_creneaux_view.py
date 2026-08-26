from datetime import datetime, timedelta, time
from django.utils.timezone import make_aware
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from adminToorrii.models import (
    Service,
    ServicePlanning,
    ServicePlanningPause,
    RDV,
    FileDattente
)
from adminToorrii.serializers import AfficherCreneauxSerializer
from rest_framework.permissions import AllowAny



class AfficherCreneauxView(APIView):
   
    permission_classes = [AllowAny]
    @extend_schema(
        tags=["Planning"],
        summary="Afficher les créneaux disponibles d’un service",
        description=(
            "Cet endpoint permet de récupérer les créneaux horaires d’un service pour une date donnée.\n\n"
            "Les créneaux peuvent être :\n"
            "- disponible\n"
            "- reserve (RDV ou file d’attente)\n"
            "- pause\n"
        ),
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Date au format YYYY-MM-DD"
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Liste des créneaux récupérée avec succès",
                response=AfficherCreneauxSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Exemple succès",
                        value={
                            "status": True,
                            "date": "2026-05-11",
                            "service_id": "SER_1",
                            "creneaux": [
                                {
                                    "debut": "09:00:00",
                                    "fin": "09:30:00",
                                    "type": "disponible"
                                },
                                {
                                    "debut": "09:30:00",
                                    "fin": "10:00:00",
                                    "type": "reserve"
                                },
                                {
                                    "debut": "10:00:00",
                                    "fin": "10:30:00",
                                    "type": "pause"
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Erreur de validation",
                examples=[
                    OpenApiExample(
                        "Date manquante",
                        value={"error": "Le paramètre 'date' est obligatoire"}
                    ),
                    OpenApiExample(
                        "Format invalide",
                        value={"error": "Format de date invalide, utilisez YYYY-MM-DD"}
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Ressource introuvable",
                examples=[
                    OpenApiExample(
                        "Service introuvable",
                        value={"error": "Service introuvable"}
                    ),
                    OpenApiExample(
                        "Planning introuvable",
                        value={"error": "Pas de planning pour ce jour"}
                    )
                ]
            )
        }
    )
    def get(self, request, service_id):

        if not service_id:
            return Response(
                {"status": False, "error": "Le service_id est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST
            )

        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"error": "Le paramètre 'date' est obligatoire"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            jour = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Format de date invalide, utilisez YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist:
            return Response(
                {"error": "Service introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        JOURS_FR = ["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI","SAMEDI","DIMANCHE"]
        weekday = JOURS_FR[jour.weekday()]

        planning = ServicePlanning.objects.filter(
            service=service,
            nom_jour=weekday
        ).first()

        if not planning:
            return Response(
                {"error": "Pas de planning pour ce jour"},
                status=status.HTTP_404_NOT_FOUND
            )

        duree = planning.service.duree_moyenne_creneau

        start = make_aware(datetime.combine(jour, planning.heure_debut_service))
        end = make_aware(datetime.combine(jour, planning.heure_fin_service))

        creneaux = []
        current = start

        while current + timedelta(minutes=duree) <= end:
            creneaux.append({
                "debut": current.time(),
                "fin": (current + timedelta(minutes=duree)).time(),
                "type": "disponible"
            })
            current += timedelta(minutes=duree)

        pauses = ServicePlanningPause.objects.filter(service_planning=planning)

        for pause in pauses:
            for c in creneaux:
                if (
                    c["debut"] < pause.heure_fin_pause and
                    c["fin"] > pause.heure_debut_pause
                ):
                    c["type"] = "pause"

        start_day = make_aware(datetime.combine(jour, time.min))
        end_day = make_aware(datetime.combine(jour, time.max))

        rdvs = RDV.objects.filter(
            service=service,
            date_heure_rdv__range=(start_day, end_day)
        )

        for rdv in rdvs:
            rdv_start = rdv.date_heure_rdv
            rdv_end = rdv_start + timedelta(minutes=rdv.duree)

            for c in creneaux:
                c_start = make_aware(datetime.combine(jour, c["debut"]))
                c_end = make_aware(datetime.combine(jour, c["fin"]))

                if (
                    c_start < rdv_end and
                    c_end > rdv_start and
                    c["type"] == "disponible"
                ):
                    c["type"] = "reserve"

        files = FileDattente.objects.filter(service=service, date_jour=jour)

        for file in files:
            file_creneau_count = file.nombre_clients

            for c in creneaux:
                if file_creneau_count > 0 and c["type"] == "disponible":
                    c["type"] = "reserve"
                    file_creneau_count -= 1

        serializer = AfficherCreneauxSerializer(creneaux, many=True)

        return Response({
            "status": True,
            "date": str(jour),
            "service_id": service_id,
            "creneaux": serializer.data
        })