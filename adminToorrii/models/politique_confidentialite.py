from django.db import models, transaction
from django.utils import timezone
from .model_counter import ModelCounter  # modèle utilitaire pour les compteurs

class PolitiqueConfidentialite(models.Model):
    politique_id = models.CharField(max_length=20, primary_key=True, editable=False, unique=True)
    titre = models.JSONField(default=list, blank=False, null=False)
    contenu = models.JSONField(default=list, blank=False, null=False)
    version = models.IntegerField(unique=True, blank=False, null=False)
    active = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    historique_modifications = models.JSONField(default=list)

    class Meta:
        verbose_name = "Politique de confidentialité"
        verbose_name_plural = "Politiques de confidentialité"

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Génération automatique du politique_id via ModelCounter
        if not self.politique_id:
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(model_name='PolitiqueConfidentialite')
            counter.last_number += 1
            counter.save(update_fields=['last_number'])
            self.politique_id = f"POL_{counter.last_number}"
            self.historique_modifications.append(f"Créé le {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.historique_modifications.append(f"Modifié le {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")

        #  Assurer qu'il n'y ait qu'une seule instance active
        if self.active:
            # Désactiver les autres politiques actives
            PolitiqueConfidentialite.objects.exclude(pk=self.pk).filter(active=True).update(active=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.politique_id} - {self.titre}"