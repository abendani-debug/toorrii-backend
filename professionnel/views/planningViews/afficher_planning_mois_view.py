import calendar
from datetime import date, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)

from adminToorrii.models import Service, ServicePlanning, ServicePlanningException
from adminToorrii.serializers import AfficherPlanningMoisSerializer
from adminToorrii.permissions import IsProfessionnelUserCustom

import logging

logger = logging.getLogger(__name__)


class AfficherPlanningMoisView(APIView):
    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel Planning"],
        summary="Afficher le planning mensuel d’un service pour un professionnel",
        description="""
Retourne le calendrier complet d’un service pour un mois donné.

Chaque jour est classé selon trois types :

- **travail** : le service est ouvert ce jour selon `ServicePlanning`.
- **repos** : le service ne travaille pas ce jour.
- **exception** : une exception est définie pour ce jour (`ServicePlanningException`).

Cet endpoint permet d'afficher le **calendrier mensuel des disponibilités d'un service**.
""",
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant unique du service (ex: SER_1)",
            ),
            OpenApiParameter(
                name="year",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Année du calendrier",
                examples=[
                    OpenApiExample(
                        "Exemple année",
                        value=2026
                    )
                ]
            ),
            OpenApiParameter(
                name="month",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Mois du calendrier (1 à 12)",
                examples=[
                    OpenApiExample(
                        "Exemple mois",
                        value=3
                    )
                ]
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Planning mensuel récupéré avec succès",
                response=AfficherPlanningMoisSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "status": True,
                            "count": 3,
                            "data": [
                                {
                                    "date": "2026-03-01",
                                    "jour": "DIMANCHE",
                                    "type": "repos"
                                },
                                {
                                    "date": "2026-03-02",
                                    "jour": "LUNDI",
                                    "type": "travail"
                                },
                                {
                                    "date": "2026-03-03",
                                    "jour": "MARDI",
                                    "type": "exception"
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Paramètres invalides",
                examples=[
                    OpenApiExample(
                        "Réponse 400",
                        value={
                            "status": False,
                            "error": "Les paramètres year et month sont obligatoires."
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Service introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={
                            "status": False,
                            "error": "Service introuvable."
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={
                            "status": False,
                            "error": "Une erreur interne est survenue."
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, service_id):

        utilisateur = request.user
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            
            year = request.query_params.get("year")
            month = request.query_params.get("month")

            if not service_id :
                return Response(
                    {"status": False, "error": "Le service_id est obligatoire."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not year or not month:
                return Response(
                    {"status": False, "error": "Les paramètres year et month sont obligatoires."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            year = int(year)
            month = int(month)

            try:
                service = Service.objects.get(pk=service_id, professionnel=professionnel)
            except Service.DoesNotExist:
                return Response(
                    {"status": False, "error": "Service introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # jours de travail du service
            planning_days = set(
                ServicePlanning.objects.filter(service=service)
                .values_list("nom_jour", flat=True)
            )

            # exceptions
            exceptions = ServicePlanningException.objects.filter(service=service)

            exception_dates = set()

            for ex in exceptions:
                current = ex.date_debut_exception
                while current <= ex.date_fin_exception:
                    exception_dates.add(current)
                    current += timedelta(days=1)

            total_days = calendar.monthrange(year, month)[1]

            result = []

            mapping = {
                "SUNDAY": "DIMANCHE",
                "MONDAY": "LUNDI",
                "TUESDAY": "MARDI",
                "WEDNESDAY": "MERCREDI",
                "THURSDAY": "JEUDI",
                "FRIDAY": "VENDREDI",
                "SATURDAY": "SAMEDI"
            }

            for day in range(1, total_days + 1):

                current_date = date(year, month, day)

                jour = mapping[current_date.strftime("%A").upper()]

                day_type = "repos"

                if jour in planning_days:
                    day_type = "travail"

                if current_date in exception_dates:
                    day_type = "exception"

                result.append({
                    "date": current_date,
                    "jour": jour,
                    "type": day_type
                })

            serializer = AfficherPlanningMoisSerializer(result, many=True)

            return Response(
                {
                    "status": True,
                    "count": len(result),
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            logger.error("Erreur dans AfficherPlanningMoisView: %s", str(e))

            return Response(
                {"status": False, "error": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )