from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import Partenaire
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiResponse

class SupprimerPartenaireView(APIView):
    """
    Endpoint pour supprimer un partenaire.
    Seuls les administrateurs actifs peuvent effectuer cette action.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Partenaire"],
        summary="Supprimer un partenaire",
        description="Supprime un partenaire existant par son `partenaire_id`. Réservé aux admins actifs.",
        responses={
            200: OpenApiResponse(description="Partenaire supprimé avec succès"),
            403: OpenApiResponse(description="Accès refusé pour les utilisateurs non-admin"),
            404: OpenApiResponse(description="Partenaire introuvable"),
            500: OpenApiResponse(description="Erreur serveur")
        }
    )
    def delete(self, request, partenaire_id):
        try:
            partenaire = Partenaire.objects.get(partenaire_id=partenaire_id)
            partenaire.delete()
            return Response(
                {"message": f"Partenaire {partenaire_id} supprimé avec succès"},
                status=status.HTTP_200_OK
            )
        except Partenaire.DoesNotExist:
            return Response(
                {"error": f"Aucun partenaire trouvé avec l'id {partenaire_id}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "Erreur serveur", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
