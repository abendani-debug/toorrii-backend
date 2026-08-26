from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter
)

from adminToorrii.models import FileDattente, Professionnel
from adminToorrii.serializers import FileDattenteSerializer
from adminToorrii.permissions import IsAdminUserCustom


class AfficherFilesDattenteParProfessionnelView(APIView):
    """
    Endpoint : Files d'attente par professionnel
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["File d'attente"],
        summary="Lister les files d’attente d’un professionnel",
        description="""
Retourne toutes les files d’attente associées à un professionnel.

### Règles :
- Vérifie que le professionnel existe
- Tri par date du jour puis file_id
- Retourne les informations complètes de chaque file

### Données retournées :
- File d'attente
- Service associé
- Professionnel
- Statut + nombre de clients
""",
        parameters=[
            OpenApiParameter(
                name="professionnel_id",
                type=str,
                location=OpenApiParameter.PATH,
                description="ID du professionnel (ex: PRF_1)",
                required=True
            )
        ],

        responses={
            200: OpenApiResponse(
                description="Liste récupérée avec succès",
                response={
                    "type": "object",
                }
            )
        },

        examples=[
            OpenApiExample(
                "Succès complet",
                response_only=True,
                value={
                    "message": "Succès",
                    "detail": "Liste des files d'attente récupérée avec succès.",
                    "count": 2,
                    "data": [
                        {
                            "file_id": "FILE_1",
                            "service_id": "SER_1",
                            "service_nom": "Consultation",
                            "professionnel_id": "PRF_1",
                            "professionnel_nom": "Clinique Alpha",
                            "date_jour": "2026-04-17",
                            "temps_moyen_attente": 15,
                            "etat_file": "En_cours",
                            "nombre_clients": 8,
                            "date_creation_FA": "2026-04-15T14:26:49.112845+0100"
                        },
                        {
                            "file_id": "FILE_2",
                            "service_id": "SER_2",
                            "service_nom": "Vaccination",
                            "professionnel_id": "PRF_1",
                            "professionnel_nom": "Clinique Alpha",
                            "date_jour": "2026-04-16",
                            "temps_moyen_attente": 10,
                            "etat_file": "En_cours",
                            "nombre_clients": 3,
                            "date_creation_FA": "2026-04-16T09:10:12.222111+0100"
                        }
                    ]
                }
            )
        ]
    )
    def get(self, request, professionnel_id, *args, **kwargs):

        if not Professionnel.objects.filter(pk=professionnel_id).exists():
            return Response(
                {
                    "message": "Erreur",
                    "detail": "Le professionnel spécifié n'existe pas."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        professionnel = Professionnel.objects.get(pk=professionnel_id)

        files = FileDattente.objects.filter(
            professionnel=professionnel
        ).order_by("date_jour", "file_id")

        serializer = FileDattenteSerializer(files, many=True)

        return Response(
            {
                "message": "Succès",
                "detail": "Liste des files d'attente récupérée avec succès.",
                "count": len(serializer.data),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )