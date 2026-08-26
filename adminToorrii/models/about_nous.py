from django.db import models, transaction
from django.utils import timezone
from . import ModelCounter

class AboutNous(models.Model):
    about_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False
    )
    titre = models.JSONField(default=dict, blank=False, null=False)
    slogan = models.JSONField(default=dict, blank=False, null=False)
    contenu = models.JSONField(default=dict, blank=False, null=False)
    mission = models.JSONField(default=dict, blank=False, null=False)
    vision = models.JSONField(default=dict, blank=False, null=False)
    valeurs = models.JSONField(default=dict, blank=False, null=False)
    pourquoi_choisir_nous = models.JSONField(default=dict, blank=False, null=False)
    qui_nous_servons = models.JSONField(default=dict, blank=False, null=False)
    version = models.IntegerField(unique=True, blank=False, null=False)
    active = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    historique_modifications = models.JSONField(default=list)

    class Meta:
        verbose_name = "À propos de nous"
        verbose_name_plural = "À propos de nous"

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Génération automatique de about_id via ModelCounter
        if not self.about_id:
            counter, created = ModelCounter.objects.select_for_update().get_or_create(
                model_name='AboutNous'
            )
            counter.last_number += 1
            counter.save(update_fields=['last_number'])
            self.about_id = f"about{counter.last_number}"

        # Historique des modifications
        if self.pk:
            self.historique_modifications.append(
                f"Modification le {timezone.now().isoformat()}"
            )
        if self.active:
            # Désactiver toutes les autres conditions
            AboutNous.objects.exclude(pk=self.pk).update(active=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.about_id} - {self.titre}"