from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.permissions import IsAuthenticated

from adminToorrii.models import RDV
from adminToorrii.serializers import CreateRDVSerializer
from adminToorrii.utils.rdv_service import RDVCreationService
from adminToorrii.permissions import IsAdminUserCustom


class ModifierRdvView(APIView):
    """
    Endpoint : Modifier un RDV existant
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["RDV"],
        summary="Modifier un RDV",
        description="""
Permet de modifier un RDV existant.
Met à jour automatiquement le ticket associé.

Contraintes vérifiées :
- Planning du service
- Pauses
- Exceptions
- Disponibilité du créneau
""",
        request=CreateRDVSerializer,
        responses={
            200: {
                "description": "Succès",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "RDV mis à jour avec succès",
                            "rdv_id": "RDV_12",
                            "ticket_id": "TKT_45",
                            "position": 5,
                            "creneau": "2026-03-12T11:00:00"
                        }
                    }
                }
            },
            400: {
                "description": "Erreur métier",
                "content": {
                    "application/json": {
                        "example": {"error": "Ce créneau est déjà réservé"}
                    }
                }
            },
            404: {
                "description": "RDV non trouvé",
                "content": {
                    "application/json": {
                        "example": {"error": "RDV non trouvé"}
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                "Exemple requête",
                summary="Modifier un RDV",
                value={
                    "date_heure_rdv": "2026-03-12T11:00:00",
                    "mode_reservation": "En_ligne",
                    "commentaire_client": "Je préfère l'après-midi"
                },
                request_only=True
            )
        ]
    )
    def patch(self, request, rdv_id):
        try:
            #  Récupérer RDV
            rdv = RDV.objects.select_related(
                "service__professionnel",
                "file_dattente"
            ).get(rdv_id=rdv_id)

        except RDV.DoesNotExist:
            return Response(
                {"error": f"RDV avec l'ID {rdv_id} non trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        #  Validation des données
        serializer = CreateRDVSerializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            #  Appel service métier
            updated_rdv, updated_ticket = RDVCreationService.update_rdv(
                rdv,
                serializer.validated_data
            )

            return Response({
                "message": "RDV mis à jour avec succès",
                "rdv_id": updated_rdv.rdv_id,
                "ticket_id": updated_ticket.ticket_id,
                "position": updated_ticket.position,
                "creneau": updated_ticket.creneau_prevue
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )