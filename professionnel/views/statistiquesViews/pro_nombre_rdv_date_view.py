from datetime import datetime
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from adminToorrii.models import RDV
from professionnel.serializers import ProRDVParDateSerializer
from adminToorrii.permissions import IsProfessionnelUserCustom


class ProRDVParDateView(APIView):
    """
    Statistiques RDV par date pour le professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel - Statistiques"],
        summary="RDV par date (Pro)",
        parameters=[
            OpenApiParameter(
                name="date",
                type=str,
                required=True,
                description="Format YYYY-MM-DD"
            )
        ],
        responses=ProRDVParDateSerializer
    )
    def get(self, request):

        date_str = request.query_params.get("date")

        if not date_str:
            return Response(
                {"detail": "Le paramètre date est obligatoire"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Format invalide YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        professionnel = request.user.professionnel

        total = RDV.objects.filter(
            service__professionnel=professionnel,
            date_heure_rdv__date=date_obj
        ).count()

        serializer = ProRDVParDateSerializer({
            "date": date_obj,
            "total_rdv": total
        })

        return Response(serializer.data, status=status.HTTP_200_OK)