from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from datetime import datetime, date, timedelta
from adminToorrii.models.model_counter import ModelCounter


class ServicePlanningPause(models.Model):

    service_planning_pause_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False
    )

    service_planning = models.ForeignKey(
        'adminToorrii.ServicePlanning',
        related_name='pauses',
        on_delete=models.CASCADE
    )

    description = models.TextField()
    heure_debut_pause = models.TimeField()
    heure_fin_pause = models.TimeField()
    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["heure_debut_pause"]
        indexes = [
            models.Index(fields=["service_planning"]),
        ]

    def clean(self):

        if self.heure_debut_pause and self.heure_fin_pause:
            if self.heure_debut_pause >= self.heure_fin_pause:
                raise ValidationError({
                    "heure_debut_pause": "Début doit être < fin",
                    "heure_fin_pause": "Fin doit être > début"
                })

        # Vérifier cohérence avec service planning
        if self.service_planning_id:
            debut_service = self.service_planning.heure_debut_service
            fin_service = self.service_planning.heure_fin_service

            if (self.heure_debut_pause < debut_service or
                self.heure_fin_pause > fin_service):
                raise ValidationError(
                    "La pause doit être incluse dans les horaires du service."
                )

        # Vérification durée minimale
        duree = datetime.combine(date.min, self.heure_fin_pause) - \
                datetime.combine(date.min, self.heure_debut_pause)

        if duree < timedelta(minutes=5):
            raise ValidationError("La pause doit durer au moins 5 minutes.")

        #  Anti-overlap (optimisé)
        overlapping = ServicePlanningPause.objects.filter(
            service_planning=self.service_planning,
            heure_debut_pause__lt=self.heure_fin_pause,
            heure_fin_pause__gt=self.heure_debut_pause
        ).exclude(pk=self.pk).select_for_update()

        if overlapping.exists():
            raise ValidationError("Cette pause chevauche une autre pause.")

    @transaction.atomic
    def save(self, *args, **kwargs):

        self.full_clean()

        if not self.service_planning_pause_id:
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                model_name="ServicePlanningPause"
            )
            counter.last_number += 1
            counter.save(update_fields=['last_number'])

            self.service_planning_pause_id = f"PLNP_{counter.last_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_planning_pause_id} - {self.service_planning}"