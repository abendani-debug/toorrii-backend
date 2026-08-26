from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField

from .model_counter import ModelCounter


class Contacte(models.Model):
    contacte_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False,
        unique=True
    )

    email = models.EmailField(max_length=100, unique=True)

    telephone_1 = PhoneNumberField(region='DZ')
    telephone_2 = PhoneNumberField(blank=True, null=True, region='DZ')
    telephone_fix = models.CharField(max_length=20, blank=True, null=True)

    adresse = models.JSONField(default=dict)
    ville = models.JSONField(default=dict)
    wilaya = models.JSONField(default=dict)

    horaires = models.CharField(max_length=255)

    site_web = models.URLField()
    facebook = models.URLField()
    instagram = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    x = models.URLField(blank=True, null=True)

    message_acceuil = models.JSONField(default=dict)

    date_creation = models.DateTimeField(default=timezone.now)
    historique_modifications = models.JSONField(default=list)

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def save(self, *args, **kwargs):
        with transaction.atomic():

            # Détection création vs modification (best practice)
            is_create = self._state.adding

            #  Empêcher plus d'une instance
            if is_create and Contacte.objects.exists():
                raise ValidationError(
                    "Il ne peut y avoir qu'un seul enregistrement dans la table Contacte."
                )

            #  Génération ID uniquement à la création
            if is_create:
                counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                    model_name='Contacte'
                )

                counter.last_number += 1
                counter.save(update_fields=['last_number'])

                self.contacte_id = f"CONTACT_{counter.last_number}"

            #  Initialisation historique (sécurité JSONField)
            if not self.historique_modifications:
                self.historique_modifications = []

            #  Historique des actions
            now_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            action = "Créé" if is_create else "Modifié"

            self.historique_modifications.append(f"{action} le {now_str}")

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contacte_id} - {self.email}"

    #  Méthode singleton (recommandée)
    @classmethod
    def get_instance(cls):
        instance = cls.objects.first()
        if not instance:
            instance = cls()
            instance.save()
        return instance