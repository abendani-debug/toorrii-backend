from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from adminToorrii.models import Service
from adminToorrii.permissions import IsAdminUserCustom

class SuspendreServiceView(APIView):
    """
    PUT /admin/Suspender_professionnels/ban/
    Suspendre un service (actif=False)
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Service"],
        summary="Suspendre un service d'un professionnel",
        description="Met le champ 'actif' à False pour un service donné.",
        responses={
            200: OpenApiResponse(description="Service suspendu avec succès"),
            404: OpenApiResponse(description="Service non trouvé")
        }
    )
    def put(self, request, service_id: str):
        try:
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist:
            return Response(
                {"detail": "Service non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        service.actif = False
        service.save()

        return Response(
            {
                "detail": "Service suspendu avec succès.",
                "service": {
                    "service_id": service.service_id,
                    "nom_service": service.nom_service,
                    "actif": service.actif
                }
            },
            status=status.HTTP_200_OK
        )
