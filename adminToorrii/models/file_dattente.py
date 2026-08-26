from django.db import models, transaction
from django.utils import timezone
from .model_counter import ModelCounter

class FileDattente(models.Model):
    ETAT_EN_COURS = "En_cours"
    ETAT_TERMINEE = "Terminee"
    ETAT_SUSPENDUE = "Suspendue"

    ETAT_CHOICES = [
        (ETAT_EN_COURS, "En cours"),
        (ETAT_TERMINEE, "Terminée"),
        (ETAT_SUSPENDUE, "Suspendue"),
    ]

    file_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False
    )

    professionnel = models.ForeignKey(
        "adminToorrii.Professionnel",
        on_delete=models.CASCADE,
        related_name="files_dattente"
    )

    service = models.ForeignKey(
        "adminToorrii.Service",
        on_delete=models.CASCADE,
        related_name="files_dattente"
    )

    date_jour = models.DateField(blank=False, null=False)
    temps_moyen_attente = models.PositiveIntegerField(help_text="En minutes", blank=False, null=False)

    etat_file = models.CharField(
        max_length=20,
        choices=ETAT_CHOICES,
        default=ETAT_EN_COURS,
        blank=False, null=False
    )
    nombre_clients = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de clients actuellement dans la file",
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["file_id"]
        verbose_name = "File d'attente"
        verbose_name_plural = "Files d'attente"
        unique_together = ["professionnel", "service", "date_jour"]
        

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.file_id:
                counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                    model_name="FILE"
                )
                counter.last_number += 1
                self.file_id = f"FILE_{counter.last_number}"
                counter.save(update_fields=['last_number'])

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_id} - {self.professionnel.nom_entreprise} ({self.date_jour})"