from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample
)

from adminToorrii.models import RDV
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import RDVNombrePresentSerializer


class RDVNombrePresentView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Statistiques"],
        summary="Nombre total des clients présents",
        description="Retourne le nombre total des rendez-vous avec statut 'Terminer'.",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                required=False,
                description="YYYY-MM-DD"
            ),
            OpenApiParameter(
                name="mois",
                type=int,
                required=False
            ),
            OpenApiParameter(
                name="annee",
                type=int,
                required=False
            ),
            OpenApiParameter(
                name="date_debut",
                type=str,
                required=False
            ),
            OpenApiParameter(
                name="date_fin",
                type=str,
                required=False
            ),
        ],
        responses={200: RDVNombrePresentSerializer},
        examples=[
            OpenApiExample(
                "Exemple",
                value={
                    "nombre_clients_presents": 85
                }
            )
        ]
    )
    def get(self, request):

        rdvs = RDV.objects.filter(statut_rdv="Terminer")

        date_str = request.query_params.get("date")
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                rdvs = rdvs.filter(date_heure_rdv__date=date_obj)
            except ValueError:
                return Response(
                    {"detail": "Format date invalide (YYYY-MM-DD)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        nombre_presents = rdvs.count()

        data = {
            "nombre_clients_presents": nombre_presents
        }

        serializer = RDVNombrePresentSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)