from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.conf import settings

from adminToorrii.models import OAuthProfessionnel, Professionnel, Utilisateur
from authentication.utils.token import (
    blacklist_existing_refresh_tokens,
    get_tokens_for_user_professionnel
)

from authentication.serializers import GoogleOAuthSerializer, CompleteProfileSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from google.oauth2 import id_token
from google.auth.transport import requests


# ==========================================================
# GOOGLE OAUTH LOGIN
# ==========================================================
class GoogleOAuthLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["OAuth Google Professionnel"],
        summary="Connexion via Google OAuth",
        description="""
Connexion intelligente avec Google OAuth.

 Fonctionnement :
1. Le frontend envoie un `id_token`
2. Vérification avec Google
3. Identification utilisateur

📌 Cas :
- Nouveau utilisateur → création
- Utilisateur classique → converti en OAuth
- Profil incomplet → onboarding
- Profil complet → connexion directe
- Compte bloqué → refus

 Sécurité :
- Access token → body
- Refresh token → cookie HttpOnly
        """,
        request=GoogleOAuthSerializer,
        responses={
            200: OpenApiResponse(
                description="Succès",
                examples=[
                    OpenApiExample(
                        name="Profil incomplet",
                        value={
                            "status": True,
                            "message": "Complétez votre profil.",
                            "access": "jwt_access_token",
                            "profile_complet": False
                        }
                    ),
                    OpenApiExample(
                        name="Connexion réussie",
                        value={
                            "status": True,
                            "message": "Connexion réussie.",
                            "access": "jwt_access_token",
                            "profile_complet": True
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Erreur",
                examples=[
                    OpenApiExample(
                        name="Token invalide",
                        value={"status": False, "message": "Token Google invalide."}
                    )
                ]
            )
        }
    )
    def post(self, request):

        serializer = GoogleOAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"status": False, "errors": serializer.errors}, status=400)

        token = serializer.validated_data["id_token"]

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            # =========================
            # Vérification email
            # =========================
            if not idinfo.get("email_verified"):
                return Response({
                    "status": False,
                    "message": "Email non vérifié par Google."
                }, status=400)

            email = idinfo.get("email")
            if not email:
                return Response({
                    "status": False,
                    "message": "Email introuvable."
                }, status=400)

            # =========================
            # Vérifier OAuth
            # =========================
            try:
                oauth_user = OAuthProfessionnel.objects.get(email=email)
                utilisateur = oauth_user.utilisateur

            except OAuthProfessionnel.DoesNotExist:

                # utilisateur classique ?
                try:
                    utilisateur = Utilisateur.objects.get(email=email)

                    oauth_user = OAuthProfessionnel.objects.create(
                        email=email,
                        profil_complet=True,
                        utilisateur=utilisateur
                    )

                except Utilisateur.DoesNotExist:
                    # nouveau utilisateur
                    utilisateur = Utilisateur.objects.create_professionnel(email=email)

                    oauth_user = OAuthProfessionnel.objects.create(
                        email=email,
                        profil_complet=False,
                        utilisateur=utilisateur
                    )

            # =========================
            # PROFIL INCOMPLET
            # =========================
            if not oauth_user.profil_complet:

                blacklist_existing_refresh_tokens(utilisateur)

                tokens = get_tokens_for_user_professionnel(utilisateur)

                response = Response({
                    "status": True,
                    "message": "Complétez votre profil.",
                    "access": tokens["access"],
                    "profile_complet": False
                }, status=200)

                response.set_cookie(
                    key="refresh_token",
                    value=tokens["refresh"],
                    httponly=True,
                    secure=True,
                    samesite='Strict',
                    max_age=30 * 24 * 60 * 60
                )

                return response

            # =========================
            # PROFIL COMPLET → vérifier professionnel
            # =========================
            try:
                pro = Professionnel.objects.get(utilisateur=utilisateur)
            except Professionnel.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Profil professionnel introuvable."
                }, status=400)

            if pro.etat_compte != "A":
                return Response({
                    "status": False,
                    "message": "Compte non autorisé."
                }, status=403)

            # =========================
            # LOGIN FINAL
            # =========================
            blacklist_existing_refresh_tokens(utilisateur)

            tokens = get_tokens_for_user_professionnel(utilisateur)

            response = Response({
                "status": True,
                "message": "Connexion réussie.",
                "access": tokens["access"],
                "profile_complet": True
            }, status=200)

            response.set_cookie(
                key="refresh_token",
                value=tokens["refresh"],
                httponly=True,
                secure=True,
                samesite='Strict',
                max_age=30 * 24 * 60 * 60
            )

            return response

        except ValueError:
            return Response({
                "status": False,
                "message": "Token Google invalide."
            }, status=400)


# ==========================================================
# COMPLETE PROFILE
# ==========================================================
class CompleteProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["OAuth Google Professionnel"],
        summary="Compléter le profil",
        description="""
Compléter le profil après connexion OAuth.

 Nécessite :
- Access token valide
 Résultat :
- Création du professionnel
- Activation du profil
- Génération nouveaux tokens
        """,
        request=CompleteProfileSerializer,
        responses={
            200: OpenApiResponse(
                description="Succès",
                examples=[
                    OpenApiExample(
                        name="Succès",
                        value={
                            "status": True,
                            "message": "Profil complété avec succès.",
                            "access": "jwt_access_token",
                            "profile_complet": True
                        }
                    )
                ]
            )
        }
    )
    def post(self, request):

        email = request.user.email

        try:
            oauth_user = OAuthProfessionnel.objects.get(email=email)
            utilisateur = oauth_user.utilisateur
        except OAuthProfessionnel.DoesNotExist:
            return Response({
                "status": False,
                "message": "Session invalide."
            }, status=400)

        serializer = CompleteProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": False,
                "errors": serializer.errors
            }, status=400)

        data = serializer.validated_data

        # =========================
        # CREATE PROFESSIONNEL
        # =========================
        Professionnel.objects.create(
            utilisateur=utilisateur,
            email=email,
            nom_entreprise=data['nom_entreprise'],
            numero_telephone=data['numero_telephone'],
            adresse=data['adresse'],
            wilaya=data['wilaya'],
            description=data['description'],
            logo=data['logo'],
            theme_couleur=data['theme_couleur']
        )

        # =========================
        # UPDATE OAUTH
        # =========================
        oauth_user.profil_complet = True
        oauth_user.save(update_fields=['profil_complet'])

        # =========================
        # TOKENS
        # =========================
        blacklist_existing_refresh_tokens(utilisateur)

        tokens = get_tokens_for_user_professionnel(utilisateur)

        response = Response({
            "status": True,
            "message": "Profil complété avec succès.",
            "access": tokens["access"],
            "profile_complet": True
        }, status=200)

        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=30 * 24 * 60 * 60
        )

        return response