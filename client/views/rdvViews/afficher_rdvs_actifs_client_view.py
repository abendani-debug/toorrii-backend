from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.utils import timezone

from adminToorrii.models import RDV, Ticket
from client.serializers import DemandeProfileClientSerializer


class AfficherRdvsActifsClientView(APIView):
    """
    Retourne les RDV actifs (En_attente / Confirmer) à venir pour un client.
    Auth : numéro de téléphone + code ticket.
    """

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = DemandeProfileClientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        numero_telephone = serializer.validated_data["numero_telephone"]
        code_ticket      = serializer.validated_data["code_ticket"]

        try:
            ticket = Ticket.objects.select_related(
                "rdv", "rdv__client"
            ).get(code_ticket=code_ticket)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket introuvable"}, status=status.HTTP_404_NOT_FOUND)

        rdv_client = ticket.rdv.client
        if str(rdv_client.numero_telephone) != str(numero_telephone):
            return Response({"error": "Accès refusé"}, status=status.HTTP_403_FORBIDDEN)

        rdvs_actifs = RDV.objects.filter(
            client=rdv_client,
            statut_rdv__in=["En_attente", "Confirmer"],
            date_heure_rdv__gte=timezone.now(),
        ).select_related("service").order_by("date_heure_rdv")

        results = []
        for rdv in rdvs_actifs:
            nom_service = rdv.service.nom_service
            # nom_service peut être un dict translatable ou une str
            if isinstance(nom_service, dict):
                nom_service = nom_service.get("fr") or nom_service.get("ar") or str(nom_service)
            results.append({
                "rdv_id":        rdv.rdv_id,
                "date_heure_rdv": rdv.date_heure_rdv,
                "statut_rdv":    rdv.statut_rdv,
                "service": {
                    "service_id":  rdv.service.service_id,
                    "nom_service": nom_service,
                },
            })

        return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)
