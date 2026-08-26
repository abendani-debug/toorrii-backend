from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse
)

from adminToorrii.permissions import IsProfessionnelUserCustom
from adminToorrii.models import Service
from professionnel.serializers import ServiceDetailSerializer


class AfficherServiceView(APIView):
    """
    GET - Liste des services du professionnel connecté
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Services - Professionnel"],
        summary="Lister tous les services du professionnel connecté",
        description=(
            "Retourne tous les services du professionnel connecté avec :\n"
            "- Planning\n"
            "- Pauses\n"
            "- Exceptions"
        ),
        responses={200: ServiceDetailSerializer(many=True)}
    )
    def get(self, request):
        try:
            # 1. Professionnel connecté
            professionnel = request.user.professionnel_profile

            # 2. Récupérer TOUS les services (PAS first)
            services = Service.objects.filter(
            professionnel=professionnel
            ).prefetch_related(
            "planning__pauses",
            "planning_exception"
            )

            # 3. Sérialisation multiple (IMPORTANT many=True)
            serializer = ServiceDetailSerializer(
                services,
                many=True,
                context={"request": request}
            )

            # 4. Response
            return Response(
                {
                    "message": "Liste des services récupérée avec succès",
                    "count": services.count(),
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {
                    "message": "Erreur serveur",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )