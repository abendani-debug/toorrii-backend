from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import FileDattente
from adminToorrii.serializers import FileDattenteDetailSerializer


class AfficherFileDattenteDetailView(APIView):

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["File d'attente"],

        summary="Détail d'une file d'attente (Admin)",

        description="""
Cet endpoint permet de récupérer toutes les informations détaillées d'une file d'attente.

---

###  Données retournées :
- Informations du service associé
- Catégorie du service
- Professionnel responsable
- Date du jour de la file
- État de la file d'attente
- Nombre de clients actuellement en attente
- Liste complète des tickets liés à cette file

---

###  Sécurité :
- Accessible uniquement aux administrateurs
- Vérification par `file_id`
""",

        parameters=[
            OpenApiParameter(
                name="file_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant unique de la file d'attente (ex: FILE_1)"
            )
        ],

        responses={
            200: OpenApiResponse(
                description="Détail de la file d'attente récupéré avec succès",
                response=FileDattenteDetailSerializer,
                examples=[
                    OpenApiExample(
                        "Exemple de réponse",
                        value={
                            "file_id": "FILE_1",
                            "categorie_nom": "Médecine générale",
                            "service_id": "SER_1",
                            "service_nom": "Consultation",
                            "professionnel_id": "PRF_1",
                            "professionnel_nom": "Clinique El Amel",
                            "date_jour": "2026-04-17",
                            "temps_moyen_attente": 15,
                            "etat_file": "En_cours",
                            "nombre_clients": 8,
                            "date_creation_FA": "2026-04-15T14:26:49.112845+01:00",
                            "tickets": [
                                {
                                    "ticket_id": "TKT_1",
                                    "position": 1,
                                    "type_ticket": "RDV",
                                    "creneau_prevue": "2026-04-17T09:00:00+01:00"
                                },
                                {
                                    "ticket_id": "TKT_2",
                                    "position": 2,
                                    "type_ticket": "RDV",
                                    "creneau_prevue": "2026-04-17T09:15:00+01:00"
                                }
                            ]
                        }
                    )
                ]
            ),

            404: OpenApiResponse(
                description="File d'attente introuvable",
                examples=[
                    OpenApiExample(
                        "Erreur file inexistante",
                        value={
                            "message": "La file d'attente spécifiée n'existe pas."
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, file_id, *args, **kwargs):

        file_obj = FileDattente.objects.select_related(
            "service",
            "service__categorie",
            "professionnel"
        ).prefetch_related(
            "tickets"
        ).filter(
            file_id=file_id
        ).first()

        if not file_obj:
            return Response(
                {"message": "La file d'attente spécifiée n'existe pas."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FileDattenteDetailSerializer(file_obj)

        return Response(
            {
                "message": "Détail de la file d'attente récupéré avec succès",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )