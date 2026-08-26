from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

from adminToorrii.models import Professionnel, ProfessionnelLead
from client.serializers import ProfessionnelFullSerializer


class ListeProfessionnelsParCategorieView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Client-Professionnels"],
        summary="Lister tous les professionnels par catégorie",
        description=(
            "Retourne les professionnels inscrits (type=inscrit) et les leads référencés (type=reference) "
            "liés à une catégorie.\n\n"
            "Chaîne logique : Catégorie → Services → Professionnels + Leads"
        ),
        responses={
            200: OpenApiResponse(description="Liste complète des professionnels et leads"),
            404: OpenApiResponse(description="Aucun résultat trouvé"),
        }
    )
    def get(self, request, categorie_id):
        results = []

        # ── 1. Pros inscrits (via leurs services) ────────────────────────────
        professionnels = Professionnel.objects.filter(
            services__categorie__categorie_id=categorie_id,
            services__actif=True,
            etat_compte=Professionnel.EtatCompte.ACTIVE
        ).distinct()

        serializer = ProfessionnelFullSerializer(professionnels, many=True)
        for item in serializer.data:
            results.append({**item, "type": "inscrit"})

        # ── 2. Pros pré-inscrits (issus du scraping) ─────────────────────────
        qs_pre = Professionnel.objects.filter(
            services__categorie__categorie_id=categorie_id,
            etat_compte=Professionnel.EtatCompte.PRE_INSCRIT,
        ).distinct()

        # Si pas de services liés, chercher via le lead lié à la catégorie
        if not qs_pre.exists():
            lead_pro_ids = ProfessionnelLead.objects.filter(
                categorie_id=categorie_id,
                professionnel__isnull=False,
            ).exclude(statut=ProfessionnelLead.StatutLead.REFUSE).values_list("professionnel_id", flat=True)

            qs_pre = Professionnel.objects.filter(
                professionnel_id__in=lead_pro_ids,
                etat_compte=Professionnel.EtatCompte.PRE_INSCRIT,
            )

        for pro in qs_pre:
            lead = ProfessionnelLead.objects.filter(professionnel=pro).first()
            results.append({
                "type":       "reference",
                "lead_id":    lead.lead_id if lead else pro.professionnel_id,
                "nom":        pro.nom_entreprise,
                "specialite": pro.description,
                "telephone":  str(pro.numero_telephone) if pro.numero_telephone else "",
                "adresse":    pro.adresse,
                "wilaya":     pro.wilaya[0] if pro.wilaya else "",
                "latitude":   lead.latitude if lead else None,
                "longitude":  lead.longitude if lead else None,
            })

        if not results:
            return Response(
                {"message": "Aucun professionnel trouvé pour cette catégorie"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)