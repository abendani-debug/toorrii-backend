"""
Management command — Scraping des salons de coiffure via Google Places API
Usage :
    python manage.py scrape_leads_coiffure --api-key=VOTRE_CLE
    python manage.py scrape_leads_coiffure --api-key=VOTRE_CLE --wilaya=Oran --dry-run
"""

import sys
import time

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from adminToorrii.models import ProfessionnelLead

TERMES_COIFFURE = [
    ("salon de coiffure",       "Salon de coiffure"),
    ("coiffeur homme",          "Coiffeur homme"),
    ("coiffeur femme",          "Coiffeur femme"),
    ("salon de coiffure et beauté", "Salon de coiffure"),
]

PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


class Command(BaseCommand):
    help = "Scrape les salons de coiffure de Google Places et les injecte dans ProfessionnelLead"

    def add_arguments(self, parser):
        parser.add_argument("--api-key", required=True, help="Clé Google Places API")
        parser.add_argument("--wilaya", default="Oran", help="Wilaya cible (défaut: Oran)")
        parser.add_argument("--categorie-id", default=None, help="ID de la catégorie Toorrii à assigner (ex: Cat_2)")
        parser.add_argument("--dry-run", action="store_true", help="Simulation sans écriture en BDD")

    def _safe(self, s: str) -> str:
        return s.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8")

    def handle(self, *args, **options):
        api_key = options["api_key"]
        wilaya = options["wilaya"]
        dry_run = options["dry_run"]
        categorie_id = options["categorie_id"]

        categorie_obj = None
        if categorie_id:
            from adminToorrii.models import Categorie
            try:
                categorie_obj = Categorie.objects.get(categorie_id=categorie_id)
                self.stdout.write(f"Categorie : {categorie_id} ({categorie_obj.nom_categorie})")
            except Categorie.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Categorie '{categorie_id}' introuvable."))
                return

        total_crees = 0
        total_ignores = 0

        for terme_recherche, label_specialite in TERMES_COIFFURE:
            self.stdout.write(self.style.MIGRATE_HEADING(self._safe(f"\n[SCRAPE] {label_specialite} -- {wilaya}")))

            query = f"{terme_recherche} {wilaya} Algérie"
            page_token = None
            page = 1

            while True:
                self.stdout.write(f"    Page {page}…")

                params = {
                    "query": query,
                    "language": "fr",
                    "key": api_key,
                    "region": "dz",
                }
                if page_token:
                    params["pagetoken"] = page_token
                    time.sleep(2)

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

                    if ProfessionnelLead.objects.filter(place_id=place_id).exists():
                        total_ignores += 1
                        continue

                    nom = place.get("name", "")
                    adresse = place.get("formatted_address", "")
                    geo = place.get("geometry", {}).get("location", {})
                    lat = geo.get("lat")
                    lng = geo.get("lng")

                    telephone = self._get_phone(api_key, place_id)

                    if dry_run:
                        self.stdout.write(self._safe(f"    [DRY-RUN] {nom} | {telephone} | {adresse} | ({lat}, {lng})"))
                        total_crees += 1
                        continue

                    with transaction.atomic():
                        ProfessionnelLead.objects.create(
                            place_id=place_id,
                            nom=nom,
                            specialite=label_specialite,
                            telephone=telephone,
                            adresse=adresse,
                            wilaya=wilaya,
                            latitude=lat,
                            longitude=lng,
                            categorie=categorie_obj,
                        )
                    total_crees += 1
                    self.stdout.write(self.style.SUCCESS(self._safe(f"    + {nom} ({telephone})")))

                    time.sleep(0.3)

                page_token = data.get("next_page_token")
                if not page_token:
                    break
                page += 1

        self.stdout.write(self._safe("\n" + "─" * 60))
        self.stdout.write(self.style.SUCCESS(f"OK  Termine -- {total_crees} crees, {total_ignores} deja presents"))

    def _get_phone(self, api_key: str, place_id: str) -> str:
        try:
            resp = requests.get(
                PLACES_DETAILS_URL,
                params={
                    "place_id": place_id,
                    "fields": "formatted_phone_number",
                    "language": "fr",
                    "key": api_key,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("result", {}).get("formatted_phone_number", "")
        except Exception:
            return ""
