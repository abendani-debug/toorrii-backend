from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from adminToorrii.models import RDV, Service
from adminToorrii.serializers import RDVStatsServiceSerializer
from adminToorrii.permissions import IsAdminUserCustom


class RDVStatsParServiceView(APIView):
    """
    Endpoint : Statistiques des rendez-vous par service (avec tous les statuts)

    Méthode : GET
    URL : /rdv/statistiques/services/{service_id}/

    Statistiques :
        - Total des RDV
        - En_attente
        - Confirmer
        - Annuler
        - Absent
        - Terminer
        - Mode de réservation
        - Source de création
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Statistiques des RDV par service (complètes)",
        description="Retourne les statistiques détaillées des rendez-vous pour un service donné (tous les statuts, modes et sources).",
        parameters=[
            OpenApiParameter(
                name="service_id",
                description="ID du service",
                required=True,
                type=str,
                location=OpenApiParameter.PATH
            )
        ],
        responses={200: RDVStatsServiceSerializer},
        examples=[
            OpenApiExample(
                "Exemple de réponse",
                value={
                    "service_id": "SER_1",
                    "service_nom": "Consultation",
                    "total_rdv": 100,
                    "rdv_par_statut": {
                        "En_attente": 20,
                        "Confirmer": 50,
                        "Annuler": 10,
                        "Absent": 5,
                        "Terminer": 15
                    },
                    "rdv_par_mode_reservation": {
                        "RDV": 70,
                        "File_attente": 30
                    },
                    "rdv_par_source_creation": {
                        "Admin": 40,
                        "Client": 60
                    }
                }
            )
        ]
    )
    def get(self, request, service_id):

        #  Vérifier que le service existe
        try:
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist:
            return Response(
                {"detail": "Service non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        #  Query des RDV du service
        rdvs = RDV.objects.filter(service=service)

        #  Total RDV
        total_rdv = rdvs.count()

        #  Stats par statut (TOUS les statuts)
        stats_statut_qs = rdvs.values("statut_rdv").annotate(
            count=Count("rdv_id")
        )

        # Dictionnaire par défaut avec tous les statuts (important)
        rdv_par_statut = {
            "En_attente": 0,
            "Confirmer": 0,
            "Annuler": 0,
            "Absent": 0,
            "Terminer": 0,
        }

        for item in stats_statut_qs:
            rdv_par_statut[item["statut_rdv"]] = item["count"]

        #  Stats par mode de réservation
        stats_mode_qs = rdvs.values("mode_reservation").annotate(
            count=Count("rdv_id")
        )
        rdv_par_mode = {
            item["mode_reservation"]: item["count"]
            for item in stats_mode_qs
        }

        #  Stats par source de création
        stats_source_qs = rdvs.values("source_creation").annotate(
            count=Count("rdv_id")
        )
        rdv_par_source = {
            item["source_creation"]: item["count"]
            for item in stats_source_qs
        }

        #  Response finale
        data = {
            "service_id": service.service_id,
            "service_nom": service.nom_service,
            "total_rdv": total_rdv,
            "rdv_par_statut": rdv_par_statut,
            "rdv_par_mode_reservation": rdv_par_mode,
            "rdv_par_source_creation": rdv_par_source,
        }

        serializer = RDVStatsServiceSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)