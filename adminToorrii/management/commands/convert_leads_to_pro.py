"""
Management command — Convertit les ProfessionnelLead en comptes Professionnel pré-inscrits.

Usage :
    python manage.py convert_leads_to_pro
    python manage.py convert_leads_to_pro --wilaya=Oran
    python manage.py convert_leads_to_pro --specialite=Cardiologue
    python manage.py convert_leads_to_pro --dry-run
"""

import re
import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from adminToorrii.models import ProfessionnelLead, Professionnel


# Couleurs par défaut selon la spécialité
COULEURS_SPECIALITE = {
    "Médecin généraliste":    "#3B82F6",
    "Cardiologue":            "#EF4444",
    "Dentiste":               "#F59E0B",
    "Pédiatre":               "#8B5CF6",
    "Gynécologue":            "#EC4899",
    "Ophtalmologue":          "#06B6D4",
    "ORL":                    "#F97316",
    "Dermatologue":           "#14B8A6",
    "Radiologue":             "#6366F1",
    "Neurologue":             "#7C3AED",
    "Orthopédiste":           "#78716C",
    "Psychiatre":             "#A855F7",
    "Pneumologue":            "#0EA5E9",
    "Gastro-entérologue":     "#10B981",
    "Urologue":               "#3B82F6",
    "Endocrinologue":         "#F59E0B",
    "Rhumatologue":           "#EF4444",
    "Clinique":               "#0F766E",
    "Polyclinique":           "#1D4ED8",
    "Laboratoire d'analyses": "#7C3AED",
    "Cabinet médical":        "#059669",
    "Chirurgien":             "#DC2626",
    "Anesthésiste":           "#6B7280",
    "Nephrologue":            "#0891B2",
    "Oncologue":              "#9333EA",
}


def _normalise_phone(raw: str) -> str | None:
    """
    Tente de convertir un numéro algérien brut en format E.164 (+213XXXXXXXXX).
    Retourne None si la conversion échoue.
    """
    if not raw:
        return None
    digits = re.sub(r"[\s\-\.\(\)]", "", raw)
    # Déjà E.164
    if digits.startswith("+213") and len(digits) == 13:
        return digits
    # Commence par 00213
    if digits.startswith("00213") and len(digits) == 14:
        return "+" + digits[2:]
    # Commence par 0 (national)
    if digits.startswith("0") and len(digits) == 10:
        return "+213" + digits[1:]
    return None


class Command(BaseCommand):
    help = "Convertit les leads scrapés en comptes Professionnel pré-inscrits (etat_compte=PRE)"

    def add_arguments(self, parser):
        parser.add_argument("--wilaya",     default=None, help="Filtrer par wilaya")
        parser.add_argument("--specialite", default=None, help="Filtrer par spécialité")
        parser.add_argument("--dry-run",    action="store_true", help="Simulation sans écriture en BDD")

    def _safe(self, s: str) -> str:
        return s.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8"
        )

    def handle(self, *args, **options):
        dry_run    = options["dry_run"]
        filtre_w   = options["wilaya"]
        filtre_s   = options["specialite"]

        qs = ProfessionnelLead.objects.filter(professionnel__isnull=True).exclude(
            statut=ProfessionnelLead.StatutLead.REFUSE
        )
        if filtre_w:
            qs = qs.filter(wilaya__iexact=filtre_w)
        if filtre_s:
            qs = qs.filter(specialite__icontains=filtre_s)

        total   = qs.count()
        created = 0
        skipped = 0

        self.stdout.write(f"{total} lead(s) a convertir...")
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY-RUN] Aucune ecriture en BDD"))

        for lead in qs:
            phone_e164 = _normalise_phone(lead.telephone)

            # Vérifier si le numéro est déjà utilisé
            if phone_e164 and Professionnel.objects.filter(numero_telephone=phone_e164).exists():
                self.stdout.write(self._safe(f"  [SKIP] {lead.nom} — telephone deja present ({phone_e164})"))
                skipped += 1
                continue

            couleur = COULEURS_SPECIALITE.get(lead.specialite, "#FF6B00")

            if dry_run:
                self.stdout.write(self._safe(
                    f"  [DRY] {lead.nom} | {lead.specialite} | {phone_e164 or 'pas de tel'}"
                ))
                created += 1
                continue

            try:
                with transaction.atomic():
                    pro = Professionnel(
                        nom_entreprise   = lead.nom,
                        email            = None,
                        numero_telephone = phone_e164,
                        adresse          = lead.adresse or "",
                        wilaya           = [lead.wilaya] if lead.wilaya else [],
                        description      = lead.specialite,
                        etat_compte      = Professionnel.EtatCompte.PRE_INSCRIT,
                        theme_couleur    = couleur,
                        utilisateur      = None,
                    )
                    pro.save()

                    # Lier le lead au compte créé
                    lead.professionnel = pro
                    lead.statut        = ProfessionnelLead.StatutLead.INSCRIT
                    lead.save(update_fields=["professionnel", "statut"])

                self.stdout.write(self.style.SUCCESS(
                    self._safe(f"  + {lead.nom} -> {pro.professionnel_id}")
                ))
                created += 1

            except Exception as e:
                self.stderr.write(self._safe(f"  [ERR] {lead.nom} : {e}"))
                skipped += 1

        self.stdout.write("\n" + "-" * 60)
        self.stdout.write(self.style.SUCCESS(
            f"Termine -- {created} crees, {skipped} ignores"
        ))
