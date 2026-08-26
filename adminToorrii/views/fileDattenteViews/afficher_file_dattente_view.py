from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiExample
from adminToorrii.permissions import IsAdminUserCustom

from adminToorrii.models import FileDattente, Service
from adminToorrii.serializers import FileDattenteSerializer


class AfficherFileDattenteView(APIView):
    """
    GET endpoint pour récupérer la liste de toutes les files d'attente.
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["File d'attente"],
        description="""
Récupère la liste complète de toutes les files d'attente.

**Vérification effectuée :**
- Aucune, retourne toutes les files existantes.
""",
        examples=[
            OpenApiExample(
                "Réponse succès",
                value={
                    "message": "Liste des files d'attente récupérée avec succès",
                    "data": [
                        {
                            "file_id": "FILE_1",
                            "service": 5,
                            "service_nom": "Massage Relaxant",
                            "professionnel": 2,
                            "professionnel_nom": "Ali Ben",
                            "date_jour": "2026-02-20",
                            "temps_moyen_attente": 15,
                            "etat_file": "En_cours",
                            "nombre_clients": 3,
                            "date_creation": "2026-02-18T12:30:00Z"
                        },
                        {
                            "file_id": "FILE_2",
                            "service": 6,
                            "service_nom": "Consultation",
                            "professionnel": 3,
                            "professionnel_nom": "Sofia K.",
                            "date_jour": "2026-02-20",
                            "temps_moyen_attente": 10,
                            "etat_file": "Terminee",
                            "nombre_clients": 2,
                            "date_creation": "2026-02-18T13:00:00Z"
                        }
                    ]
                },
                response_only=True
            )
        ],
        responses={200: FileDattenteSerializer}
    )
    def get(self, request, service_id):
        """
        Récupère toutes les files d'attente.
        """
        try:
            service = Service.objects.get(service_id=service_id)
        except Service.DoesNotExist:
                return Response(
                    {"error": "Service introuvable"},
                    status=status.HTTP_404_NOT_FOUND
                )
        files = FileDattente.objects.filter(service=service).order_by("date_jour", "file_id")
        serializer = FileDattenteSerializer(files, many=True)
        return Response(
            {
                "message": "Liste des files d'attente récupérée avec succès",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
