from django.db import models, transaction
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from adminToorrii.models import Utilisateur
from adminToorrii.models.model_counter import ModelCounter
import qrcode
from io import BytesIO
from django.core.files import File


class ProfessionnelPrioriteCounter(models.Model):
    """
    Compteur global pour gérer le dernier nombre_priorite
    des professionnels afin de garantir l'unicité.
    """
    last_priorite = models.PositiveIntegerField(default=0)
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Compteur Priorité Professionnel"
        verbose_name_plural = "Compteurs Priorité Professionnels"

    def __str__(self):
        return f"Last priorité: {self.last_priorite}"


class Professionnel(models.Model):
    """
    Modèle représentant un professionnel.

    - `professionnel_id` est généré automatiquement sous forme `pro_1`, `pro_2`, etc.
    - `nombre_priorite` est géré via ProfessionnelPrioriteCounter pour garantir l'unicité.
    """

    class EtatCompte(models.TextChoices):
        ACTIVE        = 'A',   'Active'
        SUSPENDED     = 'SUSP','Suspended'
        DELETED       = 'DEL', 'Deleted'
        PRE_INSCRIT   = 'PRE', 'Pré-inscrit'  # compte créé automatiquement depuis un lead scraping

    professionnel_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False,
        unique=True
    )

    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="professionnel_profile",
        editable=False,
        null=True,
        blank=True,
    )

    nom_entreprise = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    numero_telephone = PhoneNumberField(unique=True, region='DZ', null=True, blank=True)
    adresse = models.CharField(max_length=255, blank=True, default='')
    wilaya = models.JSONField(default=list)
    description = models.TextField(blank=True, default='')
    etat_compte = models.CharField(
        max_length=10,
        choices=EtatCompte.choices,
        default=EtatCompte.SUSPENDED
    )
    logo = models.ImageField(upload_to='professionnel/professionnel_logos/', null=True, blank=True)
    code_qr = models.ImageField(upload_to='professionnel/professionnel_code_qr/', blank=True, null=True)
    compte_verification = models.BooleanField(default=False)
    confirmation_rdv_auto = models.BooleanField(default=True)
    theme_couleur = models.CharField(max_length=20, blank=True, default='#FF6B00')
    date_inscription = models.DateTimeField(default=timezone.now)
    nombre_sms = models.IntegerField(default=0)
    nombre_priorite = models.IntegerField(default=0)

    # Email verification
    code_verification = models.CharField(max_length=6, blank=True, null=True)
    nombre_send_email = models.IntegerField(default=0)
    temp_code_verification = models.DateTimeField(null=True, blank=True)

    # Reset password
    code_verification_reset_password = models.CharField(max_length=6, blank=True, null=True)
    nombre_send_email_reset_password = models.IntegerField(default=0)
    temp_code_verification_reset_password = models.DateTimeField(null=True, blank=True)

    # Spécialité / catégorie du professionnel
    specialite = models.ForeignKey(
        'Categorie',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='professionnels',
    )

    # Champs facultatifs réseaux sociaux
    siteweb = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)

    date_creation = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom_entreprise']

    class Meta:
        verbose_name = "Professionnel"
        verbose_name_plural = "Professionnels"
        indexes = [
            models.Index(fields=['etat_compte']),
        ]

    def __str__(self):
        return self.nom_entreprise

    def generate_qr_code(self):
        """
        Génère un QR code pointant vers la page des services du professionnel.
        """
        url = f"http://localhost:3000/professionnel/{self.professionnel_id}/services"
        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        file_name = f'qr_{self.professionnel_id}.png'
        self.code_qr.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        """
        Sauvegarde atomique :
        - Génération de `professionnel_id`
        - Gestion de `nombre_priorite`
        - Génération du QR code à la création
        """
        is_new = self._state.adding

        with transaction.atomic():
            # --- Génération de professionnel_id via ModelCounter ---
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                model_name="Professionnel"
            )
            if not self.professionnel_id:
                counter.last_number += 1
                self.professionnel_id = f"pro_{counter.last_number}"
                counter.save(update_fields=['last_number'])

            # --- Gestion de nombre_priorite via ProfessionnelPrioriteCounter ---
            if self.nombre_priorite is None:
                priorite_counter, _ = ProfessionnelPrioriteCounter.objects.select_for_update().get_or_create(id=1)
                priorite_counter.last_priorite += 1
                self.nombre_priorite = priorite_counter.last_priorite
                priorite_counter.save(update_fields=['last_priorite'])

            super().save(*args, **kwargs)

            # --- Génération QR uniquement à la création ---
            if is_new:
                self.generate_qr_code()
                super().save(update_fields=['code_qr'])