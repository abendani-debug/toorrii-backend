from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from adminToorrii.models.model_counter import ModelCounter  # compteur global


# ============================
# MANAGER
# ============================

class UtilisateurManager(BaseUserManager):

    def create_admin(self, email, password=None, **extra_fields):
        return self._create_user(email, password, role='admin', is_staff=True, **extra_fields)

    def create_professionnel(self, email, password=None, **extra_fields):
        return self._create_user(email, password, role='professionnel', is_staff=False, **extra_fields)

    def _create_user(self, email, password=None, role=None, is_staff=False, **extra_fields):
        if not email:
            raise ValueError("Email obligatoire")
        email = self.normalize_email(email)

        with transaction.atomic():
            # Génération atomique utilisateur_id via ModelCounter
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(model_name="Utilisateur")
            counter.last_number += 1
            utilisateur_id = f"USR_{counter.last_number}"
            counter.save(update_fields=['last_number'])

            user = self.model(
                email=email,
                role=role,
                utilisateur_id=utilisateur_id,
                is_active=True,
                is_staff=is_staff,
                **extra_fields
            )
            user.set_password(password)
            user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        return self.create_admin(email, password, **extra_fields)


# ============================
# MODEL
# ============================

class Utilisateur(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('professionnel', 'Professionnel'),
    )

    utilisateur_id = models.CharField(max_length=20, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    date_creation = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.utilisateur_id} - {self.email}"