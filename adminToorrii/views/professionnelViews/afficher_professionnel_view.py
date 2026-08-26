from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from adminToorrii.permissions import IsAdminUserCustom
from adminToorrii.models import Professionnel
from adminToorrii.serializers import ProfessionnelSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)

PAGE_SIZE = 50


class AfficherProfessionnelView(APIView):
    permission_classes = [IsAdminUserCustom]

    @extend_schema(
        tags=["Professionnels"],
        summary="Récupérer la liste des professionnels (paginée)",
        description=(
            "Retourne les professionnels enregistrés avec pagination côté serveur.\n\n"
            "Paramètres : `page` (défaut=1), `page_size` (défaut=50), `etat` (A|SUSP|DEL|PRE|ALL)."
        ),
        parameters=[
            OpenApiParameter(name="page",      type=int, required=False, description="Numéro de page (défaut=1)"),
            OpenApiParameter(name="page_size", type=int, required=False, description="Taille de page (défaut=50, max=200)"),
            OpenApiParameter(name="etat",      type=str, required=False, description="Filtre statut : A, SUSP, DEL, PRE ou ALL"),
            OpenApiParameter(name="search",    type=str, required=False, description="Recherche par nom ou téléphone"),
            OpenApiParameter(name="categorie", type=str, required=False, description="Filtre par spécialité (categorie_id) — inclut les sous-catégories"),
        ],
        responses={
            200: OpenApiResponse(description="Liste paginée des professionnels"),
            500: OpenApiResponse(description="Erreur serveur"),
        }
    )
    def get(self, request):
        try:
            # ── Paramètres ───────────────────────────────────────────────────
            try:
                page      = max(1, int(request.query_params.get("page", 1)))
                page_size = min(200, max(1, int(request.query_params.get("page_size", PAGE_SIZE))))
            except (ValueError, TypeError):
                page, page_size = 1, PAGE_SIZE

            etat      = request.query_params.get("etat", "ALL").strip().upper()
            search    = request.query_params.get("search", "").strip()
            categorie = request.query_params.get("categorie", "").strip()

            # ── Comptages globaux (toujours sur tous les pros) ────────────────
            counts_qs = Professionnel.objects.values("etat_compte").annotate(n=Count("etat_compte"))
            counts = {row["etat_compte"]: row["n"] for row in counts_qs}
            total_global = sum(counts.values())

            # ── Queryset filtré ───────────────────────────────────────────────
            qs = Professionnel.objects.all().order_by("etat_compte", "date_creation")

            if etat != "ALL":
                qs = qs.filter(etat_compte=etat)

            if search:
                qs = qs.filter(nom_entreprise__icontains=search)

            if categorie:
                # Filtre hiérarchique : exact match + enfants niveau 2 + enfants niveau 3
                qs = qs.filter(
                    Q(specialite_id=categorie) |
                    Q(specialite__parent_id=categorie) |
                    Q(specialite__parent__parent_id=categorie)
                )

            total_filtered = qs.count()

            # ── Pagination ────────────────────────────────────────────────────
            offset  = (page - 1) * page_size
            page_qs = qs[offset: offset + page_size]

            serializer = ProfessionnelSerializer(page_qs, many=True)

            return Response(
                {
                    "status":         True,
                    "count":          total_filtered,
                    "total":          total_global,
                    "counts_by_etat": counts,
                    "page":           page,
                    "page_size":      page_size,
                    "total_pages":    max(1, -(-total_filtered // page_size)),  # ceil division
                    "data":           serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error("Erreur dans AfficherProfessionnelView: %s", str(e), exc_info=True)
            return Response(
                {"status": False, "error": "Une erreur interne est survenue.", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
