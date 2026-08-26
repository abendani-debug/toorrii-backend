from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.permissions import IsAuthenticated

from adminToorrii.models import RDV, Ticket
from adminToorrii.permissions import IsAdminUserCustom

class SupprimerRdvView(APIView):
    """
    Endpoint : Supprimer un RDV et le ticket associé.

    Méthode : DELETE
    URL : /rdv/delete/<rdv_id>/

    Description :
        Supprime le RDV identifié par `rdv_id` ainsi que le ticket associé.
        Vérifie si le RDV existe avant la suppression.
    """

    permission_classes = [ IsAdminUserCustom]

    @extend_schema(
        tags=["RDV"],
        summary="Supprimer un RDV",
        description="Supprime un RDV existant et le ticket associé en utilisant `rdv_id` comme paramètre.",
        parameters=[
            OpenApiExample(
                name="ID RDV",
                summary="Paramètre path",
                value={"rdv_id": "RDV_12"},
                request_only=True
            )
        ],
        responses={
            200: {
                "description": "RDV et ticket supprimés avec succès",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "RDV RDV_12 et ticket TKT_45 supprimés avec succès"
                        }
                    }
                }
            },
            404: {
                "description": "RDV non trouvé",
                "content": {
                    "application/json": {
                        "example": {"error": "RDV avec l'ID RDV_99 non trouvé"}
                    }
                }
            }
        }
    )
    def delete(self, request, rdv_id):
        try:
            rdv = RDV.objects.get(rdv_id=rdv_id)
        except RDV.DoesNotExist:
            return Response({"error": f"RDV avec l'ID {rdv_id} non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        rdv.delete()

        return Response({
            "message": f"RDV {rdv_id}  supprimé avec succès"
        }, status=status.HTTP_200_OK)