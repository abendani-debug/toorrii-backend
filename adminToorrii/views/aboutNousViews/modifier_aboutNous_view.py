from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.models import AboutNous
from adminToorrii.serializers import AboutNousAdminSerializer as AboutNousSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from adminToorrii.permissions import IsAdminUserCustom
import logging

logger = logging.getLogger(__name__)

class ModifierAboutNousView(APIView):
    """
    Modifier les caractéristiques de l'entreprise (Admin actif uniquement).
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["About Nous"],
        summary="Modifier les caractéristiques de l'entreprise",
        description=(
            "Permet de modifier un enregistrement 'À propos de nous'. "
            "Si le champ `active` est à True, tous les autres enregistrements seront désactivés. "
            "Accessible uniquement aux administrateurs actifs."
        ),
        request=AboutNousSerializer,
        responses={
            200: OpenApiResponse(
                description="AboutNous modifié avec succès",
                response=AboutNousSerializer,
                examples=[
                    OpenApiExample(
                        "Réponse 200",
                        value={
                            "about_id": "about2",
                            "titre": {"fr": "À propos modifié", "en": "About Us Modified", "ar": "معلومات عنا المعدلة"},
                            "slogan": {"fr": "Excellence", "en": "Excellence", "ar": "التميز"},
                            "contenu": {"fr": "Contenu FR", "en": "Content EN", "ar": "المحتوى AR"},
                            "mission": {"fr": "Mission FR", "en": "Mission EN", "ar": "المهمة AR"},
                            "vision": {"fr": "Vision FR", "en": "Vision EN", "ar": "الرؤية AR"},
                            "valeurs": {"fr": "Valeurs FR", "en": "Values EN", "ar": "قيم AR"},
                            "pourquoi_choisir_nous": {"fr": "Pourquoi FR", "en": "Why EN", "ar": "لماذا AR"},
                            "qui_nous_servons": {"fr": "Clients FR", "en": "Clients EN", "ar": "عملائنا AR"},
                            "version": 2,
                            "active": True,
                            "date_creation": "2025-12-20T16:00:00Z",
                            "historique_modifications": ["Modification le 2025-12-20T16:05:00Z"]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Données invalides",
                examples=[
                    OpenApiExample(
                        "Réponse 400",
                        value={"status": False, "message": "Données invalides", "details": {"titre": ["clé manquante 'fr'"]}}
                    )
                ]
            ),
            403: OpenApiResponse(
                description="Admin non actif ou accès refusé",
                examples=[
                    OpenApiExample(
                        "Réponse 403",
                        value={"status": False, "message": "Compte admin inactif. Action non autorisée."}
                    )
                ]
            ),
            404: OpenApiResponse(
                description="AboutNous introuvable",
                examples=[
                    OpenApiExample(
                        "Réponse 404",
                        value={"status": False, "message": "AboutNous introuvable."}
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur interne",
                examples=[
                    OpenApiExample(
                        "Réponse 500",
                        value={"status": False, "message": "Une erreur interne est survenue."}
                    )
                ]
            ),
        }
    )
    def put(self, request, about_id):
        try:
            about = AboutNous.objects.get(about_id=about_id)
        except AboutNous.DoesNotExist:
            return Response(
                {"status": False, "message": "AboutNous introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AboutNousSerializer(about, data=request.data)
        if serializer.is_valid():
            # Si le nouvel enregistrement devient actif, désactiver les autres
            if serializer.validated_data.get('active') == True:
                AboutNous.objects.exclude(about_id=about_id).update(active=False)

            serializer.save()
            return Response(
                {"status": True, "message": "AboutNous modifié avec succès", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(
            {"status": False, "message": "Données invalides", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
