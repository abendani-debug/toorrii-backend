from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from drf_spectacular.utils import extend_schema, OpenApiExample
from adminToorrii.models import Service, Professionnel
from adminToorrii.serializers import ServiceDetailSerializer

class AfficherServiceProfessionnelView(APIView):
    """
    GET endpoint pour récupérer tous les services d'un professionnel donné.

    L'ID du professionnel est fourni dans le path de l'URL.
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Service"],
        responses=ServiceDetailSerializer(many=True),
        examples=[
            OpenApiExample(
                'Liste services professionnel',
                value={
                    "message": "Liste des services du professionnel récupérée avec succès",
                    "data": [
                        {
                            "service_id": "SER_1",
                            "nom_service": "Consultation médicale",
                            "description_service": "Consultation générale",
                            "prix_service": 2500,
                            "duree_moyenne_creneau": 30,
                            "type_reservation": "R",
                            "actif": True,
                            "photo_principal": None,
                            "professionnel": "PRO_1",
                            "categorie": "CAT_1"
                        }
                    ]
                }
            )
        ]
    )
    def get(self, request, professionnel_id):
        # Vérifier que le professionnel existe
        try:
            professionnel = Professionnel.objects.get(pk=professionnel_id)
        except Professionnel.DoesNotExist:
            return Response(
                {"message": "Erreur", "detail": "Le professionnel spécifié n'existe pas."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Récupérer les services
        services = Service.objects.filter(professionnel=professionnel)
        serializer = ServiceDetailSerializer(services, many=True)

        return Response(
            {
                "message": "Liste des services du professionnel récupérée avec succès",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
