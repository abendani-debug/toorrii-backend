from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from adminToorrii.models.model_counter import ModelCounter


class ServicePlanning(models.Model):

    class jour_choix(models.TextChoices):
        DIMANCHE = 'DIMANCHE', 'Dimanche'
        LUNDI = 'LUNDI', 'Lundi'
        MARDI = 'MARDI', 'Mardi'
        MERCREDI = 'MERCREDI', 'Mercredi'
        JEUDI = 'JEUDI', 'Jeudi'
        VENDREDI = 'VENDREDI', 'Vendredi'
        SAMEDI = 'SAMEDI', 'Samedi'

    service_planning_id = models.CharField(max_length=20, primary_key=True, editable=False)

    service = models.ForeignKey(
        'adminToorrii.Service',
        related_name='planning',
        on_delete=models.CASCADE
    )

    nom_jour = models.CharField(max_length=10, choices=jour_choix.choices)

    heure_debut_service = models.TimeField()
    heure_fin_service = models.TimeField()

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["service", "nom_jour"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["service", "nom_jour"],
                name="unique_service_jour"
            )
        ]

    def clean(self):
        if self.heure_debut_service and self.heure_fin_service:
            if self.heure_debut_service >= self.heure_fin_service:
                raise ValidationError({
                    "heure_debut_service": "L'heure de début doit être < heure de fin.",
                    "heure_fin_service": "L'heure de fin doit être > heure de début."
                })

    def save(self, *args, **kwargs):
        self.full_clean()

        with transaction.atomic():

            if not self.service_planning_id:
                counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                    model_name="ServicePlanning"
                )
                counter.last_number += 1
                counter.save(update_fields=['last_number'])

                self.service_planning_id = f"PLN_{counter.last_number}"

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_planning_id} - {self.service} - {self.nom_jour}"