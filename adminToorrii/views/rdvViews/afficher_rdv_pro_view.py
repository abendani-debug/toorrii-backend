from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample

from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import RDV, Professionnel
from adminToorrii.serializers import AfficherListReservationSerializer


class AfficherRdvParProfessionnelView(APIView):
    """
    GET endpoint pour récupérer la liste de tous les rendez-vous (RDV)
    liés à un professionnel spécifique.

    Le professionnel_id doit être fourni dans le path.
    """

    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["RDV"],
        description="""
Récupère la liste complète des rendez-vous (RDV) d’un professionnel.

### Vérifications effectuées :
- Vérifie que le professionnel existe
- Retourne 404 si le professionnel n'existe pas
- Retourne une liste vide si aucun RDV n’est associé
""",
        responses={200: AfficherListReservationSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Succès - Liste des RDV",
                value={
                    "message": "Liste des RDV du professionnel récupérée avec succès",
                    "count": 2,
                    "data": [
                        {
                                    "rdv_id": "RDV_12",
                                    "client": "CLN_1 - Ahmed Benali",
                                    "client_nom": "ziad",
                                    "client_prenom": "ziad",
                                    "client_numero_telephone": "+213675902494",
                                    "client_email": "ziad@gmail.com",
                                    "service": "SER_2",
                                    "service_nom": "Consultation générale",
                                    "date_heure_rdv": "2026-03-10T10:30:00",
                                    "statut_rdv": "Confirmer",
                                    "duree": 30,
                                    "mode_reservation": "En_ligne",
                                    "actif": True,
                                    "commentaire_client": "Je préfère le matin",
                                    "ticket_id": "TKT_45",
                                    "ticket_position": 5,
                                    "ticket_creneau": "2026-03-10T10:30:00",
                                    "ticket_type": "RDV",
                                    "ticket_code": "ABC123"
                                }
                    ]
                },
                response_only=True,
            ),
            OpenApiExample(
                name="Erreur - Professionnel introuvable",
                value={
                    "message": "Erreur",
                    "detail": "Le professionnel spécifié n'existe pas."
                },
                response_only=True,
            ),
        ],
    )
    def get(self, request, professionnel_id, *args, **kwargs):
        """
        Récupérer tous les RDV liés aux services d’un professionnel.
        """

        #  Vérification stricte du professionnel (IMPORTANT)
        professionnel = get_object_or_404(
            Professionnel,
            pk=professionnel_id
        )
        print(f"{professionnel_id}")
        #  Récupération des RDV via la relation Service -> Professionnel
        rdvs = RDV.objects.filter(
            service__professionnel=professionnel
        ).select_related("service", "client").order_by("-date_heure_rdv")

        serializer = AfficherListReservationSerializer(rdvs, many=True)

        return Response(
            {
                "message": "Liste des RDV du professionnel récupérée avec succès",
                "count": rdvs.count(),
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )