"""
python manage.py seed_categories
Crée (ou met à jour) les catégories principales avec noms trilingues et couleur.
Ne supprime pas les catégories existantes.
"""
from django.core.management.base import BaseCommand
from adminToorrii.models.categorie import Categorie


CATEGORIES = [
    {
        "fr": "Santé",
        "en": "Health",
        "ar": "الصحة",
        "couleur": "#0D9488",
        "ordre": 1,
    },
    {
        "fr": "Automobile",
        "en": "Automobile",
        "ar": "السيارات",
        "couleur": "#0284C7",
        "ordre": 2,
    },
    {
        "fr": "Bien-être",
        "en": "Wellness",
        "ar": "العافية",
        "couleur": "#7C3AED",
        "ordre": 3,
    },
    {
        "fr": "Salle de sport",
        "en": "Gym & Fitness",
        "ar": "الرياضة واللياقة",
        "couleur": "#DC2626",
        "ordre": 4,
    },
    {
        "fr": "Administration",
        "en": "Administration",
        "ar": "الإدارة",
        "couleur": "#475569",
        "ordre": 5,
    },
    {
        "fr": "Coiffure & Beauté",
        "en": "Hair & Beauty",
        "ar": "الحلاقة والجمال",
        "couleur": "#EC4899",
        "ordre": 6,
    },
    {
        "fr": "Restauration",
        "en": "Food & Dining",
        "ar": "المطاعم",
        "couleur": "#F59E0B",
        "ordre": 7,
    },
    {
        "fr": "Banque & Finance",
        "en": "Banking & Finance",
        "ar": "البنوك والمالية",
        "couleur": "#15803D",
        "ordre": 8,
    },
    {
        "fr": "Éducation",
        "en": "Education",
        "ar": "التعليم",
        "couleur": "#4F46E5",
        "ordre": 9,
    },
    {
        "fr": "Immobilier",
        "en": "Real Estate",
        "ar": "العقارات",
        "couleur": "#92400E",
        "ordre": 10,
    },
    {
        "fr": "Informatique",
        "en": "IT & Technology",
        "ar": "تقنية المعلومات",
        "couleur": "#0891B2",
        "ordre": 11,
    },
    {
        "fr": "Juridique",
        "en": "Legal",
        "ar": "القانوني",
        "couleur": "#B91C1C",
        "ordre": 12,
    },
]


class Command(BaseCommand):
    help = "Seede les catégories principales trilingues"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime toutes les catégories existantes avant de créer",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            count = Categorie.objects.filter(parent=None).count()
            Categorie.objects.filter(parent=None).delete()
            self.stdout.write(self.style.WARNING(
                f"[RESET] {count} catégorie(s) racine supprimée(s)."
            ))

        created_count = 0
        updated_count = 0

        for cat_data in CATEGORIES:
            # Recherche par nom FR (insensible à la casse)
            existing = None
            for cat in Categorie.objects.filter(parent=None, active=True):
                nom = cat.nom_categorie or {}
                if nom.get("fr", "").lower() == cat_data["fr"].lower():
                    existing = cat
                    break

            nom_json = {"fr": cat_data["fr"], "en": cat_data["en"], "ar": cat_data["ar"]}

            if existing:
                existing.nom_categorie = nom_json
                existing.couleur_theme = cat_data["couleur"]
                existing.ordre_affichage = cat_data["ordre"]
                existing.active = True
                Categorie.objects.filter(pk=existing.pk).update(
                    nom_categorie=nom_json,
                    couleur_theme=cat_data["couleur"],
                    ordre_affichage=cat_data["ordre"],
                    active=True,
                )
                updated_count += 1
                self.stdout.write(f"  [MIS A JOUR] {cat_data['fr']} ({existing.categorie_id})")
            else:
                cat = Categorie(
                    nom_categorie=nom_json,
                    description_categorie={"fr": "", "en": "", "ar": ""},
                    couleur_theme=cat_data["couleur"],
                    ordre_affichage=cat_data["ordre"],
                    active=True,
                )
                cat.save()
                created_count += 1
                self.stdout.write(f"  [CREE] {cat_data['fr']} ({cat.categorie_id})")

        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] {created_count} categorie(s) creee(s), {updated_count} mise(s) a jour."
        ))
