"""
Management command — Scraping des professionnels médicaux via Google Places API
Usage :
    python manage.py scrape_leads_medicaux --api-key=VOTRE_CLE
    python manage.py scrape_leads_medicaux --api-key=VOTRE_CLE --wilaya=Oran
    python manage.py scrape_leads_medicaux --api-key=VOTRE_CLE --specialite=cardiologue
"""

import time
import sys
import io
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from adminToorrii.models import ProfessionnelLead

# ── Spécialités médicales ciblées ─────────────────────────────────────────────
SPECIALITES_MEDICALES = [
    ("médecin généraliste",             "Médecin généraliste"),
    ("cardiologue",                     "Cardiologue"),
    ("dentiste",                        "Dentiste"),
    ("pédiatre",                        "Pédiatre"),
    ("gynécologue",                     "Gynécologue"),
    ("ophtalmologue",                   "Ophtalmologue"),
    ("oto-rhino-laryngologiste ORL",    "ORL"),
    ("dermatologue",                    "Dermatologue"),
    ("radiologue",                      "Radiologue"),
    ("neurologue",                      "Neurologue"),
    ("orthopédiste",                    "Orthopédiste"),
    ("psychiatre",                      "Psychiatre"),
    ("pneumologue",                     "Pneumologue"),
    ("gastro-entérologue",              "Gastro-entérologue"),
    ("urologue",                        "Urologue"),
    ("endocrinologue",                  "Endocrinologue"),
    ("rhumatologue",                    "Rhumatologue"),
    ("clinique privée",                 "Clinique"),
    ("polyclinique",                    "Polyclinique"),
    ("laboratoire analyse médicale",    "Laboratoire d'analyses"),
    ("cabinet médical",                 "Cabinet médical"),
    ("chirurgien",                      "Chirurgien"),
    ("anesthésiste",                    "Anesthésiste"),
    ("nephrologue",                     "Nephrologue"),
    ("oncologue",                       "Oncologue"),
]

PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL     = "https://maps.googleapis.com/maps/api/place/details/json"


class Command(BaseCommand):
    help = "Scrape les professionnels médicaux de Google Places et les injecte dans ProfessionnelLead"

    def add_arguments(self, parser):
        parser.add_argument("--api-key",     required=True,  help="Clé Google Places API")
        parser.add_argument("--wilaya",      default="Oran", help="Wilaya cible (défaut: Oran)")
        parser.add_argument("--specialite",  default=None,   help="Limiter à une seule spécialité (terme de recherche)")
        parser.add_argument("--categorie-id",default=None,   help="ID de la catégorie Toorrii à assigner (ex: Cat_2)")
        parser.add_argument("--dry-run",     action="store_true", help="Simulation sans écriture en BDD")

    def _safe(self, s: str) -> str:
        """Encode safely pour les terminaux Windows (CP1252)."""
        return s.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')

    def handle(self, *args, **options):
        api_key      = options["api_key"]
        wilaya       = options["wilaya"]
        dry_run      = options["dry_run"]
        filtre_spe   = options["specialite"]
        categorie_id = options["categorie_id"]

        # Résoudre la catégorie si fournie
        categorie_obj = None
        if categorie_id:
            from adminToorrii.models import Categorie
            try:
                categorie_obj = Categorie.objects.get(categorie_id=categorie_id)
                self.stdout.write(f"Categorie : {categorie_id} ({categorie_obj.nom_categorie})")
            except Categorie.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Categorie '{categorie_id}' introuvable."))
                return

        specialites = SPECIALITES_MEDICALES
        if filtre_spe:
            specialites = [(t, l) for t, l in SPECIALITES_MEDICALES if filtre_spe.lower() in t.lower()]
            if not specialites:
                self.stderr.write(self.style.ERROR(f"Spécialité '{filtre_spe}' non trouvée dans la liste."))
                return

        total_crees  = 0
        total_ignores = 0

        for terme_recherche, label_specialite in specialites:
            self.stdout.write(self.style.MIGRATE_HEADING(self._safe(f"\n[SCRAPE] {label_specialite} -- {wilaya}")))

            query     = f"{terme_recherche} {wilaya} Algérie"
            page_token = None
            page       = 1

            while True:
                self.stdout.write(f"    Page {page}…")

                params = {
                    "query":    query,
                    "language": "fr",
                    "key":      api_key,
                    "region":   "dz",
                }
                if page_token:
                    params["pagetoken"] = page_token
                    time.sleep(2)   # Google impose un délai avant d'utiliser le nextPageToken

                try:
                    resp = requests.get(PLACES_TEXT_SEARCH_URL, params=params, timeout=15)
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"    Erreur requête: {e}"))
                    break

                api_status = data.get("status")
                if api_status not in ("OK", "ZERO_RESULTS"):
                    self.stderr.write(self.style.WARNING(f"    Statut API: {api_status} — {data.get('error_message', '')}"))
                    break

                results = data.get("results", [])
                self.stdout.write(f"    {len(results)} résultat(s)")

                for place in results:
                    place_id = place.get("place_id")
                    if not place_id:
                        continue

                    # Déjà en BDD → on passe
                    if ProfessionnelLead.objects.filter(place_id=place_id).exists():
                        total_ignores += 1
                        continue

                    nom     = place.get("name", "")
                    adresse = place.get("formatted_address", "")
                    geo     = place.get("geometry", {}).get("location", {})
                    lat     = geo.get("lat")
                    lng     = geo.get("lng")

                    # Détails : numéro de téléphone
                    telephone = self._get_phone(api_key, place_id)

                    if dry_run:
                        self.stdout.write(self._safe(f"    [DRY-RUN] {nom} | {telephone} | {adresse}"))
                        total_crees += 1
                        continue

                    with transaction.atomic():
                        ProfessionnelLead.objects.create(
                            place_id   = place_id,
                            nom        = nom,
                            specialite = label_specialite,
                            telephone  = telephone,
                            adresse    = adresse,
                            wilaya     = wilaya,
                            latitude   = lat,
                            longitude  = lng,
                            categorie  = categorie_obj,
                        )
                    total_crees += 1
                    self.stdout.write(self.style.SUCCESS(self._safe(f"    + {nom} ({telephone})")))

                    time.sleep(0.3)   # légère pause pour ne pas saturer l'API

                page_token = data.get("next_page_token")
                if not page_token:
                    break
                page += 1

        self.stdout.write(self._safe("\n" + "─" * 60))
        self.stdout.write(self.style.SUCCESS(f"OK  Termine -- {total_crees} crees, {total_ignores} deja presents"))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_phone(self, api_key: str, place_id: str) -> str:
        """Récupère le numéro de téléphone via Place Details."""
        try:
            resp = requests.get(
                PLACES_DETAILS_URL,
                params={
                    "place_id": place_id,
                    "fields":   "formatted_phone_number",
                    "language": "fr",
                    "key":      api_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("result", {}).get("formatted_phone_number", "")
        except Exception:
            return ""
