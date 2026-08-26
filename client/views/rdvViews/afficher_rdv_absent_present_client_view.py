from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.conf import settings
from django.contrib.auth import get_user_model

import jwt

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from adminToorrii.models import RDV, Ticket
from client.serializers import DemandeProfileClientSerializer


User = get_user_model()


class AfficherHistoriqueRdvClientView(APIView):
    """
    Historique des rendez-vous du client
    (Présent + Absent)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["RDV Client"],

        summary="Historique des rendez-vous (Présent + Absent)",

        description=(
            "Permet au client de consulter son historique de rendez-vous.\n\n"

            "AUTHENTIFICATION :\n"
            "1. JWT dans cookies (si connecté)\n"
            "2. Sinon fallback : numéro téléphone + code ticket\n\n"

            "STATUTS RETOURNÉS :\n"
            "- Présent\n"
            "- Absent\n\n"

            "SÉCURITÉ :\n"
            "- Un client ne voit que ses propres rendez-vous"
        ),

        request=DemandeProfileClientSerializer,

        responses={
            200: OpenApiResponse(
                description="Historique récupéré avec succès",
                examples=[
                    OpenApiExample(
                        name="Succès",
                        value={
                            "mode": "jwt",
                            "count": 2,
                            "results": [
                                {
                                    "date_heure_rdv": "2026-05-10T10:00:00",
                                    "statut_rdv": "Présent",
                                    "service": {
                                        "service_id": "SER_1",
                                        "nom_service": "Consultation"
                                    }
                                },
                                {
                                    "date_heure_rdv": "2026-05-08T09:00:00",
                                    "statut_rdv": "Absent",
                                    "service": {
                                        "service_id": "SER_2",
                                        "nom_service": "Dentiste"
                                    }
                                }
                            ]
                        },
                        response_only=True,
                        status_codes=["200"]
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur validation",
                examples=[
                    OpenApiExample(
                        name="Validation error",
                        value={
                            "numero_telephone": [
                                "Format invalide"
                            ]
                        }
                    )
                ]
            ),

            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        name="Forbidden",
                        value={
                            "error": "Accès refusé"
                        }
                    )
                ]
            ),

            404: OpenApiResponse(
                description="Aucun historique",
                examples=[
                    OpenApiExample(
                        name="Not found",
                        value={
                            "error": "Aucun historique trouvé"
                        }
                    )
                ]
            )
        }
    )
    def post(self, request):

        # =====================================================
        # 1. AUTH JWT (COOKIE)
        # =====================================================

        token = request.COOKIES.get("access_token")

        client = None

        if token:
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"]
                )

                client_id = payload.get("client_id")

                client = User.objects.filter(
                    id=client_id
                ).first()

            except jwt.ExpiredSignatureError:
                client = None
            except jwt.InvalidTokenError:
                client = None

        # =====================================================
        # 2. FALLBACK AUTH (TÉLÉPHONE + TICKET)
        # =====================================================

        if not client:

            serializer = DemandeProfileClientSerializer(
                data=request.data
            )

            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            numero_telephone = serializer.validated_data[
                "numero_telephone"
            ]

            code_ticket = serializer.validated_data[
                "code_ticket"
            ]

            try:
                ticket = Ticket.objects.select_related(
                    "rdv",
                    "rdv__client"
                ).get(code_ticket=code_ticket)

            except Ticket.DoesNotExist:
                return Response(
                    {"error": "Ticket introuvable"},
                    status=status.HTTP_404_NOT_FOUND
                )

            rdv_client = ticket.rdv.client

            if str(rdv_client.numero_telephone) != str(numero_telephone):
                return Response(
                    {"error": "Accès refusé"},
                    status=status.HTTP_403_FORBIDDEN
                )

            client = rdv_client

        # =====================================================
        # 3. HISTORIQUE RDV
        # =====================================================

        historique = RDV.objects.filter(
            client=client,
            statut_rdv__in=["Présent", "Absent"]
        ).order_by("-date_heure_rdv")

        if not historique.exists():
            return Response(
                {"error": "Aucun historique trouvé"},
                status=status.HTTP_404_NOT_FOUND
            )

        results = []

        for r in historique:
            results.append({
                "date_heure_rdv": r.date_heure_rdv,
                "statut_rdv": r.statut_rdv,
                "service": {
                    "service_id": r.service.service_id,
                    "nom_service": getattr(r.service, "nom_service", None)
                }
            })

        return Response(
            {
                "mode": "jwt" if token else "ticket",
                "count": len(results),
                "results": results
            },
            status=status.HTTP_200_OK
        )