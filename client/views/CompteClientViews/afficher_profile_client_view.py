from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from client.utils.jwt_token import generate_token_client

from adminToorrii.models import Client, Ticket

from client.serializers import (
    DemandeProfileClientSerializer,
    AfficherProfileClientSerializer
)


class AfficherProfileClientView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Client Profile"],

        summary="Afficher le profil client",

        description=(
            "Permet à un client d'accéder à son profil via un système "
            "d'authentification basé sur un numéro de téléphone "
            "et un code ticket valide.\n\n"

            "Fonctionnement :\n"
            "1. Si un cookie `refresh_token` valide existe déjà, "
            "le profil client est retourné automatiquement.\n\n"

            "2. Sinon, le système vérifie :\n"
            "• le numéro de téléphone\n"
            "• le code ticket\n\n"

            "3. Si les informations sont valides :\n"
            "• un nouveau refresh token est généré\n"
            "• le token est stocké dans un cookie HttpOnly sécurisé\n"
            "• le profil client est retourné.\n\n"

            "Mesures de sécurité :\n"
            "• Cookie HttpOnly\n"
            "• Cookie Secure HTTPS\n"
            "• SameSite Strict\n"
            "• Validation du ticket\n"
            "• Vérification de l'état du ticket"
        ),

        request=DemandeProfileClientSerializer,

        examples=[
            OpenApiExample(
                name="Exemple Requête",
                summary="Authentification via ticket",
                description=(
                    "Le client fournit son numéro de téléphone "
                    "et un code ticket valide."
                ),
                value={
                    "numero_telephone": "+213699112233",
                    "code_ticket": "CTK-20260507-0001"
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
                    "Profil client récupéré avec succès.\n\n"

                    "Cas possibles :\n"
                    "• Session déjà active via refresh token valide\n"
                    "• Authentification réussie via ticket"
                ),

                examples=[

                    OpenApiExample(
                        name="Succès",
                        summary="Profil récupéré avec succès",

                        value={
                            "nom": "Benali",
                            "prenom": "Ziad",
                            "email": "ziad@example.com",
                            "numero_telephone": "+213699112233",
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

                description=(
                    "Données invalides.\n\n"

                    "Causes possibles :\n"
                    "• numéro téléphone invalide\n"
                    "• code ticket invalide\n"
                    "• champs manquants"
                ),

                examples=[

                    OpenApiExample(
                        name="Numéro invalide",

                        value={
                            "message": "Données invalides",
                            "errors": {
                                "numero_telephone": [
                                    "Le numéro de téléphone est invalide."
                                ]
                            }
                        },

                        response_only=True,
                        status_codes=["400"]
                    ),

                    OpenApiExample(
                        name="Code ticket manquant",

                        value={
                            "message": "Données invalides",
                            "errors": {
                                "code_ticket": [
                                    "Ce champ est obligatoire."
                                ]
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
                    "• ticket expiré\n"
                    "• ticket annulé\n"
                    "• ticket n'appartient pas au client\n"
                    "• ticket invalide"
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

                    OpenApiExample(
                        name="Ticket non autorisé",

                        value={
                            "message": "Ticket introuvable ou non autorisé"
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

                description="Client introuvable.",

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

            # =====================================================
            # SERVER ERROR
            # =====================================================

            500: OpenApiResponse(

                description="Erreur interne du serveur",

                examples=[

                    OpenApiExample(
                        name="Erreur serveur",

                        value={
                            "message": "Une erreur interne est survenue."
                        },

                        response_only=True,
                        status_codes=["500"]
                    ),
                ]
            ),
        }
    )
    def post(self, request):

        # =====================================================
        # 1) Vérification refresh token cookie
        # =====================================================

        cookie_refresh = request.COOKIES.get("refresh_token")

        if cookie_refresh:

            try:
                refresh = RefreshToken(cookie_refresh)

                # Vérification type token
                if refresh.payload.get("token_type") != "refresh":
                    raise TokenError("Invalid token type")

                client_id = refresh.get("client_id")

                client = Client.objects.filter(
                    id_client=client_id
                ).first()

                if client:

                    data = {
                        "nom": client.nom,
                        "prenom": client.prenom,
                        "email": client.email,
                        "numero_telephone": str(client.numero_telephone),
                        "date_inscription": client.date_inscription,
                    }

                    return Response(
                        AfficherProfileClientSerializer(data).data,
                        status=status.HTTP_200_OK
                    )

            except TokenError:
                pass

        # =====================================================
        # 2) Validation données request
        # =====================================================

        serializer = DemandeProfileClientSerializer(data=request.data)

        if not serializer.is_valid():

            return Response(
                {
                    "message": "Données invalides",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        numero = serializer.validated_data['numero_telephone']
        code_ticket = serializer.validated_data['code_ticket']

        # =====================================================
        # 3) Vérification client
        # =====================================================

        client = Client.objects.filter(
            numero_telephone=numero
        ).first()

        if not client:

            return Response(
                {"message": "Client introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # =====================================================
        # 4) Vérification ticket
        # =====================================================

        ticket = Ticket.objects.filter(
            code_ticket=code_ticket,
            client=client
        ).first()

        if not ticket:

            return Response(
                {"message": "Ticket introuvable ou non autorisé"},
                status=status.HTTP_403_FORBIDDEN
            )

        # =====================================================
        # 5) Vérification état ticket
        # =====================================================

        if ticket.etat_ticket in [
            Ticket.EtatTicket.ANNULER,
            Ticket.EtatTicket.EXPIRER
        ]:

            return Response(
                {"message": "Ticket expiré ou annulé"},
                status=status.HTTP_403_FORBIDDEN
            )

        # =====================================================
        # 6) Génération nouveaux tokens
        # =====================================================

        tokens = generate_token_client(client)

        # =====================================================
        # 7) Données profil
        # =====================================================

        data = {
            "nom": client.nom,
            "prenom": client.prenom,
            "email": client.email,
            "numero_telephone": str(client.numero_telephone),
            "date_inscription": client.date_inscription,
        }

        response = Response(
            AfficherProfileClientSerializer(data).data,
            status=status.HTTP_200_OK
        )

        # =====================================================
        # 8) Sauvegarde refresh token cookie
        # =====================================================

        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=60 * 60 * 24 * 30  # 30 jours
        )

        return response