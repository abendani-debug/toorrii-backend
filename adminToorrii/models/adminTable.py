from django.db import models, transaction
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from .utilisateur import Utilisateur
from . import ModelCounter

# ============================
# MANAGER
# ============================

class AdminManager(BaseUserManager):
    def create_admin(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email obligatoire")

        email = self.normalize_email(email)

        with transaction.atomic():  # Tout se fait atomiquement
            # 1 Génération admin_id via ModelCounter
            counter, created = ModelCounter.objects.select_for_update().get_or_create(
                model_name='AdminUser'
            )
            counter.last_number += 1
            counter.save(update_fields=['last_number'])
            generated_admin_id = f"ADM{counter.last_number}"
            extra_fields['admin_id'] = generated_admin_id

            # 2 Création AdminUser
            admin = self.model(email=email, **extra_fields)
            admin.set_password(password)
            admin.save(using=self._db)

            # 3 Création de l'utilisateur lié
            utilisateur = Utilisateur.objects.create_admin(email=email, password=password)
            admin.utilisateur = utilisateur
            admin.save(update_fields=['utilisateur'])

            return admin

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('est_super_admin', True)
        extra_fields.setdefault('niveau_acces', 'Super_A')
        return self.create_admin(email, password, **extra_fields)


# ============================
# MODEL
# ============================

class AdminUser(AbstractBaseUser):
    admin_id = models.CharField(max_length=20, primary_key=True, editable=False)
    utilisateur = models.OneToOneField(
        'adminToorrii.Utilisateur',
        on_delete=models.CASCADE,
        null=True,
        related_name="admin_profile"
    )
    nom = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    numero_telephone = PhoneNumberField(unique=True, region='DZ')
    date_creation = models.DateTimeField(default=timezone.now)
    list_derniers_activites = models.JSONField(default=list)
    est_super_admin = models.BooleanField(default=False)
    niveau_acces = models.CharField(
        max_length=20,
        choices=[
            ('Super_A', 'Super Admin'),
            ('A_general', 'Admin General'),
            ('Moderateur', 'Moderateur'),
        ],
        default='Super_A'
    )
    etat_compte = models.CharField(
        max_length=10,
        choices=[
            ('A', 'Active'),
            ('SUSP', 'Suspended'),
            ('DEL', 'Deleted'),
        ],
        default='A'
    )

    # reset password
    code_verification_reset_password = models.CharField(max_length=6, blank=True, null=True)
    nombre_send_email_reset_password = models.IntegerField(default=0)
    temp_code_verification_reset_password = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = AdminManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.nom} ({self.admin_id})"