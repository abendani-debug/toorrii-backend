from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Professionnel
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
import logging
from adminToorrii.utils.brevo_service import send_professionnel_notification_désactivation

logger = logging.getLogger(__name__)


class DesactiverProfessionnelView(APIView):
    """
    Endpoint pour désactiver un compte professionnel.
    Accessible uniquement par un administrateur.
    """
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Professionnels"],
        summary="Désactiver un compte professionnel",
        description=(
            "Permet à un administrateur de désactiver un compte professionnel.\n\n"
            " Fonctionnement :\n"
            "- Recherche du professionnel via `professionnel_id`\n"
            "- Vérifie si le compte est déjà désactivé\n"
            "- Désactive le compte (`etat_compte = 'I'` ou `inactive`)\n"
            "- Envoie un email de notification (non bloquant)\n\n"
            " Sécurité :\n"
            "- Endpoint protégé (Admin uniquement)\n\n"
            " Retour :\n"
            "- Statut succès\n"
            "- Indicateur d’envoi email"
        ),
        parameters=[
            OpenApiParameter(
                name="professionnel_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant unique du professionnel à désactiver"
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Professionnel désactivé avec succès",
                examples=[
                    OpenApiExample(
                        name="Succès",
                        summary="Désactivation réussie",
                        value={
                            "status": True,
                            "message": "Compte professionnel désactivé avec succès.",
                            "email_sent": True,
                            "professionnel_id": "PRO_1"
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Compte déjà désactivé",
                examples=[
                    OpenApiExample(
                        name="Déjà désactivé",
                        value={
                            "status": False,
                            "message": "Le compte est déjà désactivé."
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="Professionnel introuvable",
                examples=[
                    OpenApiExample(
                        name="Non trouvé",
                        value={
                            "status": False,
                            "message": "Professionnel introuvable."
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                description="Erreur serveur",
                examples=[
                    OpenApiExample(
                        name="Erreur interne",
                        value={
                            "status": False,
                            "error": "Une erreur interne est survenue."
                        }
                    )
                ]
            ),
        }
    )
    def put(self, request, professionnel_id):
        try:
            # =========================
            # Récupérer le professionnel
            # =========================
            try:
                pro = Professionnel.objects.get(professionnel_id=professionnel_id)
            except Professionnel.DoesNotExist:
                return Response(
                    {"status": False, "message": "Professionnel introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # =========================
            # Vérifier si déjà désactivé
            # =========================
            if pro.etat_compte != 'A':
                return Response(
                    {"status": False, "message": "Le compte est déjà désactivé."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # =========================
            # Désactivation
            # =========================
            pro.etat_compte = 'SUSP'  # 
            pro.save(update_fields=["etat_compte"])

            email_sent = True

            # =========================
            # Envoi email (non bloquant)
            # =========================
            try:
                send_professionnel_notification_désactivation(
                    email=pro.email,
                    nom=pro.nom_entreprise
                )
            except Exception as email_error:
                email_sent = False
                logger.warning(
                    "Échec envoi email | professionnel=%s | erreur=%s",
                    pro.email,
                    str(email_error)
                )

            # =========================
            # Réponse succès
            # =========================
            return Response(
                {
                    "status": True,
                    "message": "Compte professionnel désactivé avec succès.",
                    "email_sent": email_sent,
                    "professionnel_id": pro.professionnel_id
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("Erreur dans DesactiverProfessionnelView: %s", str(e))
            return Response(
                {"status": False, "error": "Une erreur interne est survenue."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )