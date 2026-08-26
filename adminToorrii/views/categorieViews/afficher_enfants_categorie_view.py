from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Categorie
from adminToorrii.serializers import CategorieAfficherSerializer
import logging

logger = logging.getLogger(__name__)


class AfficherEnfantsCategorieView(APIView):
    permission_classes = [IsAdminUserCustom]

    def get(self, request, parent_id):
        try:
            try:
                parent = Categorie.objects.get(categorie_id=parent_id)
            except Categorie.DoesNotExist:
                return Response({
                    "status": False,
                    "message": f"Catégorie '{parent_id}' introuvable."
                }, status=status.HTTP_404_NOT_FOUND)

            enfants = Categorie.objects.filter(parent=parent).order_by("ordre_affichage")

            serializer = CategorieAfficherSerializer(enfants, many=True)
            return Response({
                "status": True,
                "parent_id": parent_id,
                "count": enfants.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Erreur dans AfficherEnfantsCategorieView : %s", str(e))
            return Response({
                "status": False,
                "error": "Une erreur interne est survenue. Veuillez réessayer plus tard."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
