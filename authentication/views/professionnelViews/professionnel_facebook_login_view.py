from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import requests

from django.conf import settings
from adminToorrii.models import Utilisateur, OAuthProfessionnel, Professionnel
from authentication.serializers import FacebookOAuthSerializer
from authentication.utils.facebookOauth import verify_facebook_token, blacklist_existing_refresh_tokens
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


class FacebookOAuthLoginView(APIView):
    """
    Endpoint pour connexion via Facebook OAuth pour les professionnels.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["OAuth Facebook Professionnel"],
        summary="Connexion intelligente avec Facebook",
        description=(
            "Permet à un professionnel de se connecter via Facebook OAuth.\n\n"
            "Fonctionnement :\n"
            "1. Vérifie le `access_token` Facebook\n"
            "2. Récupère email et ID Facebook\n"
            "3. Vérifie OAuthProfessionnel\n\n"
            "Cas possibles :\n"
            "✔ Nouveau utilisateur → création + profil incomplet\n"
            "✔ Utilisateur existant classique → ajout OAuth\n"
            "✔ Profil incomplet → onboarding\n"
            "✔ Profil complet + actif → connexion directe\n"
            "Profil bloqué → accès refusé\n\n"
            "Sécurité :\n"
            "- Access token → body\n"
            "- Refresh token → cookie HttpOnly (30 jours)"
        ),
        request=FacebookOAuthSerializer,
        responses={
            200: OpenApiResponse(
                description="Succès (login ou onboarding)",
                examples=[
                    OpenApiExample(
                        name="Nouveau utilisateur",
                        summary="Création + onboarding",
                        value={
                            "status": True,
                            "message": "Compte créé, complétez votre profil.",
                            "access": "...",
                            "profile_complet": False
                        },
                        response_only=True
                    ),
                    OpenApiExample(
                        name="Profil incomplet",
                        summary="Continuer onboarding",
                        value={
                            "status": True,
                            "message": "Complétez votre profil.",
                            "access": "...",
                            "profile_complet": False
                        },
                        response_only=True
                    ),
                    OpenApiExample(
                        name="Connexion réussie",
                        summary="Utilisateur actif",
                        value={
                            "status": True,
                            "message": "Connexion réussie.",
                            "access": "...",
                            "profile_complet": True
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Erreur (token ou email)",
                examples=[
                    OpenApiExample(
                        name="Token invalide",
                        value={"status": False, "message": "Token Facebook invalide."},
                        response_only=True
                    ),
                    OpenApiExample(
                        name="Email manquant",
                        value={"status": False, "message": "Facebook email introuvable."},
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        name="Compte bloqué",
                        value={"status": False, "message": "Compte non autorisé."},
                        response_only=True
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur communication avec Facebook",
                examples=[
                    OpenApiExample(
                        name="Erreur API",
                        value={"status": False, "message": "Erreur communication avec Facebook."},
                        response_only=True
                    )
                ]
            )
        }
    )
    def post(self, request):
        serializer = FacebookOAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": False, "errors": serializer.errors}, status=400)

        access_token = serializer.validated_data["access_token"]

        # Vérifier token Facebook
        if not verify_facebook_token(access_token):
            return Response({"status": False, "message": "Token Facebook invalide."}, status=400)

        try:
            # Récupérer données utilisateur Facebook
            fb_response = requests.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,email,first_name,last_name,picture",
                    "access_token": access_token
                }
            )

            if fb_response.status_code != 200:
                return Response({"status": False, "message": "Token Facebook invalide ou expiré."}, status=400)

            data = fb_response.json()
            facebook_id = data.get("id")
            email = data.get("email")

            if not facebook_id:
                return Response({"status": False, "message": "Facebook ID introuvable."}, status=403)

            if not email:
                return Response({"status": False, "message": "Facebook email introuvable. Autorisez l'accès à votre email."}, status=403)

            identifier = email

            # CAS 1 : utilisateur OAuth existant
            try:
                oauth_user = OAuthProfessionnel.objects.get(email=identifier)
                utilisateur = oauth_user.utilisateur

            except OAuthProfessionnel.DoesNotExist:
                # CAS 2 : utilisateur existant classique
                try:
                    utilisateur = Utilisateur.objects.get(email=identifier)
                    oauth_user = OAuthProfessionnel.objects.create(
                        email=identifier,
                        profil_complet=True,
                        utilisateur=utilisateur
                    )
                except Utilisateur.DoesNotExist:
                    # CAS 3 : nouvel utilisateur OAuth
                    utilisateur = Utilisateur.objects.create_professionnel(email=identifier, is_active=True)
                    oauth_user = OAuthProfessionnel.objects.create(
                        email=identifier,
                        profil_complet=False,
                        utilisateur=utilisateur
                    )

            # Profil incomplet
            if not oauth_user.profil_complet:
                blacklist_existing_refresh_tokens(utilisateur)
                refresh = RefreshToken.for_user(utilisateur)
                response = Response({
                    "status": True,
                    "message": "Complétez votre profil.",
                    "access": str(refresh.access_token),
                    "profile_complet": False
                }, status=200)
                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=True,
                    samesite='Strict',
                    max_age=30*24*60*60
                )
                return response

            # Vérifier professionnel actif
            try:
                pro = Professionnel.objects.get(utilisateur=utilisateur)
            except Professionnel.DoesNotExist:
                return Response({"status": False, "message": "Profil professionnel introuvable."}, status=400)

            if pro.etat_compte != "A":
                return Response({"status": False, "message": "Compte non autorisé."}, status=403)

            # Login final
            blacklist_existing_refresh_tokens(utilisateur)
            refresh = RefreshToken.for_user(utilisateur)
            response = Response({
                "status": True,
                "message": "Connexion réussie.",
                "access": str(refresh.access_token),
                "profile_complet": True
            }, status=200)
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=30*24*60*60
            )
            return response

        except requests.RequestException:
            return Response({"status": False, "message": "Erreur communication avec Facebook."}, status=500)