from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample
)

from adminToorrii.models import FileDattente
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import FileDattenteSerializer


class AfficherListeFileDattenteView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["File d'attente"],
        summary="Lister toutes les files d'attente",
        description="""
Cet endpoint permet de récupérer la liste complète des files d'attente.

 Informations retournées :
- Identifiant de la file
- Service associé
- Professionnel responsable
- Date du jour
- État de la file (En cours, Terminée, Suspendue)
- Nombre de clients dans la file

 Tri :
- Du plus récent au plus ancien

 Accès :
- Réservé aux administrateurs
""",

        responses={
            200: OpenApiResponse(
                description="Liste des files d'attente récupérée avec succès",
                response=FileDattenteSerializer(many=True),
                examples=[
                    OpenApiExample(
                        "Exemple de réponse",
                        value=[
                            {
                                "file_id": "FILE_1",
                                "service": 1,
                                "service_id": "SER_1",
                                "service_nom": "Consultation générale",
                                "professionnel": 3,
                                "professionnel_id": "PRF_1",
                                "professionnel_nom": "Clinique El Amel",
                                "date_jour": "2026-04-17",
                                "temps_moyen_attente": 15,
                                "etat_file": "En_cours",
                                "nombre_clients": 8,
                                "date_creation_FA": "2026-04-17T08:00:00Z"
                            },
                            {
                                "file_id": "FILE_2",
                                "service": 2,
                                "service_id": "SER_2",
                                "service_nom": "Dentiste",
                                "professionnel": 5,
                                "professionnel_id": "PRF_2",
                                "professionnel_nom": "Cabinet Smile",
                                "date_jour": "2026-04-16",
                                "temps_moyen_attente": 20,
                                "etat_file": "Terminee",
                                "nombre_clients": 12,
                                "date_creation_FA": "2026-04-16T10:00:00Z"
                            }
                        ]
                    )
                ]
            )
        }
    )
    def get(self, request):

        files = FileDattente.objects.select_related(
            "service",
            "professionnel"
        ).order_by("-date_jour")

        serializer = FileDattenteSerializer(files, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)