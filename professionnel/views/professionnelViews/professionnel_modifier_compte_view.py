from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from adminToorrii.models import Professionnel
from professionnel.serializers import ProfessionnelSerializer
from adminToorrii.permissions import IsProfessionnelUserCustom


class ProfessionnelModifierCompteView(APIView):
    """
    Endpoint pour modifier les informations du professionnel connecté.
    """

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["Professionnel"],
        summary="Modifier profil professionnel",
        description=(
            "Permet au professionnel connecté de modifier ses informations.\n\n"
            " Sécurité :\n"
            "- Authentification requise (JWT)\n"
            "- Accessible uniquement aux professionnels actifs et vérifiés\n\n"
            " Champs NON modifiables :\n"
            "- professionnel_id\n"
            "- utilisateur\n"
            "- email\n"
            "- etat_compte\n"
            "- code_qr\n"
        ),
        request=ProfessionnelSerializer,
        responses={
            200: OpenApiResponse(
                response=ProfessionnelSerializer,
                description="Profil mis à jour avec succès"
            ),
            400: OpenApiResponse(description="Erreur de validation"),
            401: OpenApiResponse(description="Non authentifié"),
            403: OpenApiResponse(description="Accès refusé"),
            404: OpenApiResponse(description="Profil professionnel introuvable"),
        },
        examples=[
            OpenApiExample(
                name="Exemple requête",
                summary="Modification profil",
                value={
                    "nom_entreprise": "Salon Elite",
                    "numero_telephone": "+213555123456",
                    "adresse": "Oran Centre",
                    "description": "Salon moderne haut de gamme",
                    "theme_couleur": "blue"
                },
                request_only=True
            ),
            OpenApiExample(
                name="Succès",
                summary="Réponse succès",
                value={
                    "nom_entreprise": "Salon Elite",
                    "numero_telephone": "+213555123456",
                    "adresse": "Oran Centre",
                    "description": "Salon moderne haut de gamme",
                    "theme_couleur": "blue"
                },
                response_only=True,
                status_codes=["200"]
            )
        ]
    )
    def put(self, request):
        try:
            #  récupérer le professionnel connecté
            professionnel = request.user.professionnel_profile

        except Professionnel.DoesNotExist:
            return Response(
                {"message": "Profil professionnel introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        #  update partiel (PATCH-like)
        serializer = ProfessionnelSerializer(
            professionnel,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if not serializer.is_valid():
            return Response(
                {
                    "message": "Erreur de validation",
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            {
                "message": "Profil mis à jour avec succès",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )