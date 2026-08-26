from django.db import models, transaction
from django.utils import timezone
from adminToorrii.models.model_counter import ModelCounter  # compteur global

class RDV(models.Model):
    """
    Modèle Rendez-vous
    """

    STATUT_RDV_CHOICES = [
        ("En_attente", "En attente"),
        ("Confirmer", "Confirmé"),
        ("Annuler", "Annulé"),
        ("Terminer", "Terminé"),
        ("Absent", "Absent"),
    ]

    MODE_RESERVATION_CHOICES = [
        ("En_ligne", "En ligne"),
        ("Sur_place", "Sur place"),
    ]

    SOURCE_CREATION_CHOICES = [
        ("Client", "Client"),
        ("Pro", "Professionnel"),
        ("Admin", "Administrateur"),
    ]

    rdv_id = models.CharField(
        primary_key=True,
        max_length=20,
        editable=False
    )

    client = models.ForeignKey(
        "adminToorrii.Client",
        on_delete=models.PROTECT,
        related_name="rdvs",
        null=True,
        blank=True
    )

    service = models.ForeignKey(
        "adminToorrii.Service",
        on_delete=models.CASCADE,
        related_name="rdvs"
    )
    file_dattente = models.ForeignKey(
        "adminToorrii.FileDattente",
        on_delete=models.CASCADE,
        related_name="files"
    )

    date_heure_rdv = models.DateTimeField(blank=False, null=False)
    duree = models.PositiveIntegerField(help_text="Durée en minutes", blank=False, null=False)

    statut_rdv = models.CharField(
        max_length=20,
        choices=STATUT_RDV_CHOICES,
    )

    mode_reservation = models.CharField(
        max_length=20,
        choices=MODE_RESERVATION_CHOICES,
        blank=False,
        null=False,
        default="En_ligne"
    )

    commentaire_client = models.TextField(blank=True, null=True)
    actif = models.BooleanField(blank=False, null=False, default=False)

    source_creation = models.CharField(
        max_length=20,
        choices=SOURCE_CREATION_CHOICES,
        blank=False,
        null=False
    )

    mail_envoye = models.BooleanField(blank=False, null=False, default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        constraints = [
            # Un seul RDV par service et créneau (évite le double booking global)
            models.UniqueConstraint(
                fields=["service", "date_heure_rdv"],
                name="unique_service_creneau"
            ),
            # Un client ne peut pas réserver deux fois le même service au même créneau
            models.UniqueConstraint(
                fields=["client", "service", "date_heure_rdv"],
                name="unique_rdv_client_creneau"
            )
        ]

    def save(self, *args, **kwargs):
        """
        Génération atomique rdv_id via ModelCounter : RDV_1, RDV_2, ...
        """
        with transaction.atomic():
            if not self.rdv_id:
                counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                    model_name="RDV"
                )
                counter.last_number += 1
                self.rdv_id = f"RDV_{counter.last_number}"
                counter.save(update_fields=['last_number'])

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rdv_id} - {self.client} - {self.service}"