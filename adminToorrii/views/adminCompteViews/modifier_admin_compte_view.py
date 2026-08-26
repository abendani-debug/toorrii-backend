from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from adminToorrii.models import AdminUser, Utilisateur
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.serializers import (
    AdminAccountModifierSerializer,
    AdminAccountModifierPasswordSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
import logging

logger = logging.getLogger(__name__)

class ModifierAdminCompteView(APIView):
    """
    Endpoint pour modifier les informations du compte Admin lié à l'utilisateur connecté.
    Authentification JWT obligatoire.
    - Email non modifiable
    - Si le mot de passe change :
        - L'ancien refresh token fourni est blacklisté
        - Un nouveau refresh token est placé dans un cookie HttpOnly (30 jours)
        - L'access token est renvoyé dans la réponse JSON
        - L'instance Utilisateur liée est mise à jour
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Admin compte"],
        summary="Modifier les informations du compte Admin",
        description=(
            "Permet à l'administrateur connecté de modifier ses informations personnelles.\n"
            "Si le mot de passe est modifié, l'ancien refresh token fourni sera blacklisté, "
            "un nouveau refresh token sera placé dans un cookie HttpOnly (30 jours), "
            "et le access token sera retourné dans la réponse JSON.\n"
            "Le mot de passe est également synchronisé avec l'instance Utilisateur liée."
        ),
        request=AdminAccountModifierPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Compte mis à jour avec succès",
                examples=[
                    OpenApiExample(
                        name="Mot de passe changé",
                        summary="Exemple réussite avec rotation token",
                        value={
                            "status": True,
                            "message": "Compte mis à jour avec succès",
                            "data": {
                                "admin_id": "ADM123",
                                "email": "admin@test.com",
                                "nom": "John Doe",
                                "numero_telephone": "+213660000000"
                            },
                            "new_tokens": {
                                "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                            }
                        },
                        response_only=True
                    ),
                    OpenApiExample(
                        name="Mot de passe non changé",
                        summary="Exemple réussite sans rotation token",
                        value={
                            "status": True,
                            "message": "Compte mis à jour avec succès",
                            "data": {
                                "admin_id": "ADM123",
                                "email": "admin@test.com",
                                "nom": "John Doe",
                                "numero_telephone": "+213660000000"
                            }
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(description="Erreur de validation"),
            401: OpenApiResponse(description="Non authentifié"),
            500: OpenApiResponse(description="Erreur serveur")
        }
    )
    def put(self, request):
        # Récupère le profil admin lié à l'utilisateur connecté
        admin: AdminUser = getattr(request.user, "admin_profile", None)
        if not admin:
            return Response(
                {"status": False, "message": "Profil Admin introuvable pour cet utilisateur."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Choix du serializer selon présence du mot de passe
        serializer_class = AdminAccountModifierPasswordSerializer if "password" in request.data else AdminAccountModifierSerializer
        serializer = serializer_class(admin, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Erreur de validation",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        password_changed = "password" in serializer.validated_data

        # Données de réponse de base
        response_data = {
            "status": True,
            "message": "Compte mis à jour avec succès",
            "data": {
                "admin_id": admin.admin_id,
                "email": admin.email,
                **{k: v for k, v in serializer.validated_data.items() if k != "refresh" and k != "password"}
            }
        }

        # Rotation token si mot de passe changé
        if password_changed:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response({"error": "Refresh token manquant"}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                # Blacklist ancien refresh token
                old_refresh = RefreshToken(refresh_token)
                old_refresh.blacklist()

                # Génération nouveau refresh token
                new_refresh = RefreshToken.for_user(request.user)
                access_token = str(new_refresh.access_token)

                # Sauvegarde mot de passe
                serializer.save()
                # Synchronisation avec l'instance Utilisateur
                try:
                    utilisateur = request.user
                    utilisateur.password = make_password(serializer.validated_data["password"])
                    utilisateur.save(update_fields=['password'])
                except Exception as e:
                    logger.warning("Impossible de mettre à jour Utilisateur lié: %s", e)

                # Réponse avec cookie HttpOnly pour refresh
                response = Response({
                    **response_data,
                    "new_tokens": {"access": access_token}
                }, status=status.HTTP_200_OK)
                response.set_cookie(
                    key="refresh_token",
                    value=str(new_refresh),
                    httponly=True,
                    secure=True,
                    samesite='Strict',
                    max_age=30*24*60*60  # 30 jours
                )

                return response

            except Exception as e:
                logger.error("Erreur rotation token: %s", e)
                return Response({
                    "status": False,
                    "message": "Refresh token invalide ou déjà blacklisté.",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        # Si mot de passe non changé
        serializer.save()
        return Response(response_data, status=status.HTTP_200_OK)