from django.db import models, transaction
from django.utils import timezone
from .model_counter import ModelCounter  # modèle utilitaire pour les compteurs

class ConditionDutilisation(models.Model):
    condition_id = models.CharField(
        max_length=20,
        primary_key=True,
        unique=True,
        editable=False
    )
    titre = models.JSONField(default=list, blank=False, null=False)
    contenu = models.JSONField(default=list, blank=False, null=False)
    version = models.IntegerField(unique=True, blank=False, null=False)
    date_creation = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)
    historique_modifications = models.JSONField(default=list)

    class Meta:
        db_table = "condition_dutilisation"

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Génération automatique de condition_id via ModelCounter
        if not self.condition_id:
            counter, created = ModelCounter.objects.select_for_update().get_or_create(
                model_name='ConditionDutilisation'
            )
            counter.last_number += 1
            counter.save(update_fields=['last_number'])
            self.condition_id = f"COND_{counter.last_number}"

        # Historique des modifications
        now_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.pk:
            self.historique_modifications.append(f"Modifié le {now_str}")
        else:
            self.historique_modifications.append(f"Créé le {now_str}")

        #  Vérification : une seule condition active à la fois
        if self.active:
            # Désactiver toutes les autres conditions
            ConditionDutilisation.objects.exclude(pk=self.pk).update(active=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.condition_id} - {self.titre}"