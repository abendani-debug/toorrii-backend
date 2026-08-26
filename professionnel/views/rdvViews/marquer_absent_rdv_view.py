from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
    OpenApiParameter
)

from adminToorrii.models import RDV, Professionnel
from adminToorrii.permissions import IsProfessionnelUserCustom


class MarquerAbsentRdvProView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["RDV Professionnel"],
        summary="Marquer un RDV comme absent",
        description=(
            "Permet à un professionnel de marquer un rendez-vous comme absent.\n\n"
            " Fonctionnalités :\n"
            "- Vérifie que le RDV appartient au professionnel\n"
            "- Met à jour le statut → Absent\n"
            "- Le RDV doit être en statut 'Confirmer' pour être marqué absent\n\n"
            " Sécurité :\n"
            "- Le RDV doit appartenir à un service du professionnel connecté\n"
        ),

        parameters=[
            OpenApiParameter(
                name="rdv_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID du RDV (ex: RDV_1)"
            )
        ],

        responses={
            200: OpenApiResponse(
                description="RDV marqué comme absent",
                examples=[
                    OpenApiExample(
                        "Succès",
                        value={
                            "message": "RDV marqué comme absent avec succès",
                            "statut": "Absent"
                        }
                    )
                ]
            ),

            400: OpenApiResponse(
                description="Erreur métier",
                examples=[
                    OpenApiExample(
                        "Statut invalide",
                        value={"error": "Impossible de marquer absent ce RDV (statut invalide)"}
                    )
                ]
            ),

            403: OpenApiResponse(
                description="Accès refusé",
                examples=[
                    OpenApiExample(
                        "Non autorisé",
                        value={"detail": "Vous n'avez pas la permission d'effectuer cette action."}
                    )
                ]
            ),

            404: OpenApiResponse(
                description="RDV introuvable ou non autorisé",
                examples=[
                    OpenApiExample(
                        "RDV non trouvé",
                        value={"error": "RDV introuvable ou non autorisé"}
                    ),
                    OpenApiExample(
                        "Profil professionnel introuvable",
                        value={"error": "Profil professionnel introuvable."}
                    )
                ]
            )
        }
    )
    def patch(self, request, rdv_id):

        utilisateur = request.user

        # Récupérer professionnel
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Récupérer RDV avec sécurité
        try:
            rdv = RDV.objects.select_related("service").get(
                rdv_id=rdv_id,
                service__professionnel=professionnel
            )
        except RDV.DoesNotExist:
            return Response(
                {"error": "RDV introuvable ou non autorisé"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérification du statut
        if rdv.statut_rdv not in ("Confirmer", "En_attente"):
            return Response(
                {"error": "Impossible de marquer absent ce RDV (statut invalide)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Logique métier
        try:
            rdv.statut_rdv = "Absent"
            rdv.save()

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "RDV marqué comme absent avec succès",
                "statut": rdv.statut_rdv
            },
            status=status.HTTP_200_OK
        )
