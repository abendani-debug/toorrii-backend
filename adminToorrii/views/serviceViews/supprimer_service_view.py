from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from adminToorrii.models import Service
from adminToorrii.permissions import IsAdminUserCustom

class SupprimerServiceView(APIView):
    """
    DELETE /admin/professionnels/{id}/
    Supprimer définitivement un service d'un professionnel
    """
    permission_classes = [IsAdminUserCustom]
    @extend_schema(
        tags=["Service"],
        summary="Supprimer un service d'un professionnel",
        description="Supprime définitivement un service existant par son service_id",
        responses={
            200: OpenApiResponse(description="Service supprimé avec succès"),
            404: OpenApiResponse(description="Service non trouvé")
        }
    )
    def delete(self, request, service_id):
        try:
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist:
            return Response(
                {"detail": "Service non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )

        service.delete()
        return Response(
            {"detail": "Service supprimé avec succès."},
            status=status.HTTP_200_OK
        )
