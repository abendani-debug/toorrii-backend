from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from datetime import datetime, date
from adminToorrii.models.model_counter import ModelCounter


class ServicePlanningException(models.Model):

    service_planning_exception_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False
    )

    service = models.ForeignKey(
        'adminToorrii.Service',
        related_name='planning_exception',
        on_delete=models.CASCADE
    )

    raison = models.TextField()
    raison_autre = models.TextField(blank=True, null=True)

    date_debut_exception = models.DateField()
    date_fin_exception = models.DateField()

    heure_debut_exception = models.TimeField()
    heure_fin_exception = models.TimeField()

    date_creation = models.DateTimeField(default=timezone.now, editable=False)

    def clean(self):

        # 1. validation dates
        if self.date_debut_exception > self.date_fin_exception:
            raise ValidationError({
                "date_debut_exception": "Début doit être <= fin",
                "date_fin_exception": "Fin doit être >= début"
            })

        # 2. validation heures
        if self.heure_debut_exception and self.heure_fin_exception:
            if self.heure_debut_exception >= self.heure_fin_exception:
                raise ValidationError({
                    "heure_debut_exception": "Début doit être < fin",
                    "heure_fin_exception": "Fin doit être > début"
                })

        # 3. vérification overlap exceptions
        overlapping = ServicePlanningException.objects.filter(
            service=self.service,
            date_debut_exception__lte=self.date_fin_exception,
            date_fin_exception__gte=self.date_debut_exception,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Cette exception chevauche une autre exception existante.")

    @transaction.atomic
    def save(self, *args, **kwargs):

        self.full_clean()

        if not self.service_planning_exception_id:
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                model_name="ServicePlanningException"
            )
            counter.last_number += 1
            counter.save(update_fields=['last_number'])

            self.service_planning_exception_id = f"PLNE_{counter.last_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_planning_exception_id} - {self.service}"