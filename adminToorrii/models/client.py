from django.db import models, transaction
from django.utils import timezone
import secrets
from phonenumber_field.modelfields import PhoneNumberField
from .model_counter import ModelCounter


class Client(models.Model):
    """
    Client authentifié uniquement par TOKEN (pas de mot de passe)
    """

    id_client = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False
    )

    nom = models.CharField(max_length=50, null=True, blank= True)
    prenom = models.CharField(max_length=50, null=True, blank= True)

    email = models.EmailField(blank=True, null=True)

    numero_telephone = PhoneNumberField(unique=True, region='DZ')

    date_inscription = models.DateTimeField(default=timezone.now)

    actif = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date_inscription"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.id_client:
                counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                    model_name="Client"
                )
                counter.last_number += 1
                self.id_client = f"CLN_{counter.last_number}"
                counter.save(update_fields=['last_number'])

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_client} - {self.nom} ({self.prenom})"
