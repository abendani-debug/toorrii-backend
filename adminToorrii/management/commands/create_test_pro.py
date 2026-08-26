"""
Commande de création d'un compte professionnel de test.

Usage :
    python manage.py create_test_pro
    python manage.py create_test_pro --email test@toorrii.com --password monmdp123
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
from adminToorrii.models.utilisateur import Utilisateur
from adminToorrii.models.professionnel import Professionnel
import io


def _make_placeholder_logo(color=(13, 148, 136)):
    """Génère un PNG 200x200 de couleur unie sans dépendance Pillow obligatoire."""
    try:
        from PIL import Image
        img = Image.new("RGB", (200, 200), color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # Fallback : PNG 1x1 pixel encodé en dur
        return bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
            0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
            0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
            0x44, 0xAE, 0x42, 0x60, 0x82,
        ])


class Command(BaseCommand):
    help = "Crée un compte professionnel de test (email+password déjà vérifiés, compte actif)"

    def add_arguments(self, parser):
        parser.add_argument("--email",    default="test.pro@toorrii.com")
        parser.add_argument("--password", default="Test1234!")
        parser.add_argument("--company",  default="Toorrii Test Business")
        parser.add_argument("--phone",    default="+213550000001")

    def handle(self, *args, **options):
        email    = options["email"]
        password = options["password"]
        company  = options["company"]
        phone    = options["phone"]

        # Vérifier si le compte existe déjà
        if Utilisateur.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(
                f"Un compte existe déjà pour {email}. Supprimez-le d'abord si vous voulez le recréer."
            ))
            return

        with transaction.atomic():
            # 1. Créer l'utilisateur
            user = Utilisateur.objects.create_professionnel(
                email=email,
                password=password,
            )

            # 2. Créer le professionnel
            pro = Professionnel(
                utilisateur=user,
                nom_entreprise=company.upper(),
                email=email,
                numero_telephone=phone,
                adresse="123 Rue de Test, Oran",
                wilaya=["Oran"],
                description="Compte de test créé automatiquement pour les tests de développement.",
                etat_compte=Professionnel.EtatCompte.ACTIVE,
                compte_verification=True,   # email déjà vérifié
                confirmation_rdv_auto=True,
                theme_couleur="#0d9488",
                nombre_priorite=None,       # sera auto-assigné par le save()
            )

            # Logo placeholder
            logo_bytes = _make_placeholder_logo()
            pro.logo.save("test_logo.png", ContentFile(logo_bytes), save=False)

            pro.save()

        self.stdout.write(self.style.SUCCESS("[OK] Compte professionnel de test cree avec succes !"))
        self.stdout.write(f"   Email    : {email}")
        self.stdout.write(f"   Password : {password}")
        self.stdout.write(f"   ID Pro   : {pro.professionnel_id}")
        self.stdout.write(f"   ID User  : {user.utilisateur_id}")
        self.stdout.write(f"   Statut   : ACTIVE / Vérifié")
