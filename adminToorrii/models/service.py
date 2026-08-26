from django.db import models, transaction
from django.utils import timezone
from adminToorrii.models.model_counter import ModelCounter  # compteur global


class Service(models.Model):


    class TypeReservation(models.TextChoices):
        F = 'F', 'File d`attente'
        R = 'R', 'Rendez-vous'
        FR = 'FR', 'File d`attente et Rendez-vous'

    service_id = models.CharField(
        max_length=20,
        primary_key=True,
        editable=False
    )
    professionnel = models.ForeignKey('adminToorrii.Professionnel', related_name='services', on_delete=models.CASCADE)
    categorie = models.ForeignKey('adminToorrii.Categorie', related_name='services', on_delete=models.PROTECT)
    nom_service = models.CharField(max_length=100)
    description_service = models.TextField()
    prix_service = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    duree_moyenne_creneau = models.PositiveIntegerField()
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now, editable=False)
    photo_principal = models.ImageField(
        upload_to="services/photos_principal",
        blank=True,
        null=True
    )
    type_reservation = models.CharField(
        max_length=25,
        choices=TypeReservation.choices
    )

    def save(self, *args, **kwargs):
        if not self.service_id:
            with transaction.atomic():
                # Génération atomique via ModelCounter
                counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                    model_name="Service"
                )
                counter.last_number += 1
                self.service_id = f"SER_{counter.last_number}"
                counter.save(update_fields=['last_number'])

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_id} - {self.nom_service}"