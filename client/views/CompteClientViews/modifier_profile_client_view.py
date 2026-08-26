from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from adminToorrii.models import Client, Ticket

from client.serializers import (
    ModifierProfileClientSerializer,
    AfficherProfileClientSerializer
)


class ModifierProfileClientView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Client Profile"],

        summary="Modifier le profil client",

        description=(
            "Cette API permet au client de modifier ses informations personnelles.\n\n"

            " MÉTHODE D'AUTHENTIFICATION :\n"
            "1. Si un `refresh_token` valide existe dans les cookies → accès direct\n"
            "2. Sinon, authentification via :\n"
            "   - numéro de téléphone\n"
            "   - code ticket valide\n\n"

            " RÈGLES :\n"
            "• Le ticket doit appartenir au client\n"
            "• Le ticket doit être actif (non expiré / non annulé)\n"
            "• Tous les champs sont optionnels sauf identification\n\n"

            " SÉCURITÉ :\n"
            "• Cookie HttpOnly\n"
            "• Cookie Secure (HTTPS)\n"
            "• SameSite Strict\n"
            "• Validation ticket"
        ),

        request=ModifierProfileClientSerializer,

        examples=[
            OpenApiExample(
                name="Requête avec ticket",
                summary="Modification via ticket",
                description="Cas où le client n'a pas encore de session active",
                value={
                    "numero_telephone": "+213699112233",
                    "code_ticket": "CTK-20260507-0001",
                    "nom": "Benali",
                    "prenom": "Ali",
                    "email": "ali@example.com",
                    "nouveau_numero_telephone": "+213777888999"
                },
                request_only=True,
            ),

            OpenApiExample(
                name="Requête avec session",
                summary="Modification via refresh_token cookie",
                description="Aucun ticket requis si session active",
                value={
                    "nom": "Benali",
                    "prenom": "Ali",
                    "email": "ali@example.com"
                },
                request_only=True,
            ),
        ],

        responses={

            # =====================================================
            # SUCCESS
            # =====================================================

            200: OpenApiResponse(
                response=AfficherProfileClientSerializer,

                description=(
                    "Profil client modifié avec succès.\n\n"
                    "Deux cas possibles :\n"
                    "• modification via session active (refresh token)\n"
                    "• modification via ticket + numéro"
                ),

                examples=[
                    OpenApiExample(
                        name="Succès",

                        value={
                            "nom": "Benali",
                            "prenom": "Ali",
                            "email": "ali@example.com",
                            "numero_telephone": "+213777888999",
                            "date_inscription": "2026-05-07T10:30:00Z"
                        },

                        response_only=True,
                        status_codes=["200"]
                    ),
                ]
            ),

            # =====================================================
            # BAD REQUEST
            # =====================================================

            400: OpenApiResponse(
                description="Données invalides",

                examples=[
                    OpenApiExample(
                        name="Erreur validation",

                        value={
                            "message": "Données invalides",
                            "errors": {
                                "email": ["Enter a valid email address."]
                            }
                        },

                        response_only=True,
                        status_codes=["400"]
                    ),
                ]
            ),

            # =====================================================
            # FORBIDDEN
            # =====================================================

            403: OpenApiResponse(
                description=(
                    "Accès refusé.\n\n"
                    "Causes possibles :\n"
                    "• ticket invalide\n"
                    "• ticket expiré\n"
                    "• ticket annulé\n"
                    "• ticket non lié au client"
                ),

                examples=[
                    OpenApiExample(
                        name="Ticket expiré",

                        value={
                            "message": "Ticket expiré ou annulé"
                        },

                        response_only=True,
                        status_codes=["403"]
                    ),
                ]
            ),

            # =====================================================
            # NOT FOUND
            # =====================================================

            404: OpenApiResponse(
                description="Client introuvable",

                examples=[
                    OpenApiExample(
                        name="Client inexistant",

                        value={
                            "message": "Client introuvable"
                        },

                        response_only=True,
                        status_codes=["404"]
                    ),
                ]
            ),
        }
    )
    def post(self, request):

        # =====================================================
        # SESSION CHECK (refresh token cookie)
        # =====================================================

        cookie_refresh = request.COOKIES.get("refresh_token")

        if cookie_refresh:

            try:
                refresh = RefreshToken(cookie_refresh)

                if refresh.payload.get("token_type") != "refresh":
                    raise TokenError()

                client_id = refresh.get("client_id")

                client = Client.objects.filter(
                    id_client=client_id
                ).first()

                if client:

                    if "nom" in request.data:
                        client.nom = request.data["nom"]

                    if "prenom" in request.data:
                        client.prenom = request.data["prenom"]

                    if "email" in request.data:
                        client.email = request.data["email"]

                    if "nouveau_numero_telephone" in request.data:
                        client.numero_telephone = request.data["nouveau_numero_telephone"]

                    client.save()

                    return Response(
                        AfficherProfileClientSerializer({
                            "nom": client.nom,
                            "prenom": client.prenom,
                            "email": client.email,
                            "numero_telephone": str(client.numero_telephone),
                            "date_inscription": client.date_inscription,
                        }).data,
                        status=status.HTTP_200_OK
                    )

            except TokenError:
                pass

        # =====================================================
        # FALLBACK AUTH (ticket)
        # =====================================================

        serializer = ModifierProfileClientSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "message": "Données invalides",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        numero = serializer.validated_data["numero_telephone"]
        code_ticket = serializer.validated_data["code_ticket"]

        client = Client.objects.filter(
            numero_telephone=numero
        ).first()

        if not client:
            return Response(
                {"message": "Client introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        ticket = Ticket.objects.filter(
            code_ticket=code_ticket,
            client=client
        ).first()

        if not ticket:
            return Response(
                {"message": "Ticket invalide ou non autorisé"},
                status=status.HTTP_403_FORBIDDEN
            )

        if ticket.etat_ticket in [
            Ticket.EtatTicket.ANNULER,
            Ticket.EtatTicket.EXPIRER
        ]:
            return Response(
                {"message": "Ticket expiré ou annulé"},
                status=status.HTTP_403_FORBIDDEN
            )

        # UPDATE
        client.nom = serializer.validated_data.get("nom", client.nom)
        client.prenom = serializer.validated_data.get("prenom", client.prenom)
        client.email = serializer.validated_data.get("email", client.email)

        if "nouveau_numero_telephone" in serializer.validated_data:
            client.numero_telephone = serializer.validated_data["nouveau_numero_telephone"]

        client.save()

        return Response(
            AfficherProfileClientSerializer({
                "nom": client.nom,
                "prenom": client.prenom,
                "email": client.email,
                "numero_telephone": str(client.numero_telephone),
                "date_inscription": client.date_inscription,
            }).data,
            status=status.HTTP_200_OK
        )