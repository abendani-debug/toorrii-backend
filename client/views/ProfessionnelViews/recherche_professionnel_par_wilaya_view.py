from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.permissions import AllowAny
from adminToorrii.models import Professionnel, ProfessionnelLead
from client.serializers import ProfessionnelFullSerializer


class RechercherProfessionnelParWilayaView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Client-Professionnels"],
        summary="Rechercher des professionnels par wilaya",
        description=(
            "Retourne les professionnels inscrits (type=inscrit) "
            "et les professionnels référencés/scrapés (type=reference) pour une wilaya donnée."
        ),
        parameters=[
            OpenApiParameter(name="wilaya", description="Nom de la wilaya (ex: Oran)", required=True, type=str),
            OpenApiParameter(name="specialite", description="Filtrer par spécialité (ex: Cardiologue)", required=False, type=str),
            OpenApiParameter(name="page", type=int, required=False, description="Numéro de page pour les leads (défaut=1)"),
            OpenApiParameter(name="page_size", type=int, required=False, description="Taille de page pour les leads (défaut=50, max=200)"),
        ],
        responses={
            200: OpenApiResponse(description="Liste des professionnels trouvés"),
            400: OpenApiResponse(description="Paramètre wilaya manquant"),
        }
    )
    def get(self, request):

        wilaya     = request.query_params.get("wilaya", "").strip()
        specialite = request.query_params.get("specialite", "").strip()

        if not wilaya:
            return Response(
                {"message": "Le paramètre wilaya est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            page      = max(1, int(request.query_params.get("page", 1)))
            page_size = min(200, max(1, int(request.query_params.get("page_size", 50))))
        except (ValueError, TypeError):
            page, page_size = 1, 50

        wilaya_upper = wilaya.upper()
        results = []

        # ── 1. Pros inscrits (toujours sur la 1ère page uniquement) ─────────
        if page == 1:
            qs_inscrits = Professionnel.objects.filter(
                wilaya__contains=[wilaya_upper],
                etat_compte=Professionnel.EtatCompte.ACTIVE
            )
            serializer = ProfessionnelFullSerializer(qs_inscrits, many=True)
            for item in serializer.data:
                results.append({**item, "type": "inscrit"})

        # ── 2. Pros pré-inscrits (issus du scraping, via leur lead) ─────────
        lead_qs = ProfessionnelLead.objects.filter(
            wilaya__iexact=wilaya,
            professionnel__isnull=False,
            professionnel__etat_compte=Professionnel.EtatCompte.PRE_INSCRIT,
        ).exclude(statut=ProfessionnelLead.StatutLead.REFUSE).select_related("professionnel")

        # Leads pas encore convertis
        raw_lead_qs = ProfessionnelLead.objects.filter(
            wilaya__iexact=wilaya,
            professionnel__isnull=True,
        ).exclude(statut=ProfessionnelLead.StatutLead.REFUSE)

        if specialite:
            lead_qs     = lead_qs.filter(specialite__icontains=specialite)
            raw_lead_qs = raw_lead_qs.filter(specialite__icontains=specialite)

        # ── Pagination des leads (potentiellement volumineux) ───────────────
        # lead_qs et raw_lead_qs sont paginés comme une seule liste continue,
        # sans les matérialiser entièrement en mémoire.
        total_leads = lead_qs.count() + raw_lead_qs.count()
        offset = (page - 1) * page_size

        n_leads = lead_qs.count()
        if offset < n_leads:
            lead_qs     = lead_qs[offset: offset + page_size]
            remaining   = page_size - (min(offset + page_size, n_leads) - offset)
            raw_lead_qs = raw_lead_qs[:remaining] if remaining > 0 else raw_lead_qs.none()
        else:
            raw_offset  = offset - n_leads
            lead_qs     = lead_qs.none()
            raw_lead_qs = raw_lead_qs[raw_offset: raw_offset + page_size]

        for lead in lead_qs:
            pro = lead.professionnel
            results.append({
                "type":       "reference",
                "lead_id":    lead.lead_id,
                "nom":        pro.nom_entreprise,
                "specialite": lead.specialite,
                "telephone":  str(pro.numero_telephone) if pro.numero_telephone else lead.telephone,
                "adresse":    pro.adresse or lead.adresse,
                "wilaya":     lead.wilaya,
                "latitude":   lead.latitude,
                "longitude":  lead.longitude,
            })

        for lead in raw_lead_qs:
            results.append({
                "type":       "reference",
                "lead_id":    lead.lead_id,
                "nom":        lead.nom,
                "specialite": lead.specialite,
                "telephone":  lead.telephone,
                "adresse":    lead.adresse,
                "wilaya":     lead.wilaya,
                "latitude":   lead.latitude,
                "longitude":  lead.longitude,
            })

        if not results:
            return Response(
                {"message": "Aucun professionnel trouvé pour cette wilaya"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "count":        len(results),
                "total_leads":  total_leads,
                "page":         page,
                "page_size":    page_size,
                "total_pages":  max(1, -(-total_leads // page_size)),
                "results":      results,
            },
            status=status.HTTP_200_OK,
        )