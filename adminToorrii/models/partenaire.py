from django.db import models, transaction
from django.utils import timezone
from django.db.models import F, Max
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from .model_counter import ModelCounter


class Partenaire(models.Model):

    partenaire_id = models.CharField(
        max_length=20,
        primary_key=True,
        unique=True,
        editable=False
    )

    nom_partenaire = models.JSONField(default=dict)
    logo = models.ImageField(upload_to='partenaire/partenaire_logos/')
    description = models.JSONField(default=dict)
    adresse = models.JSONField(default=dict)

    email = models.EmailField(unique=True)
    telephone = PhoneNumberField()
    site_web = models.URLField()

    date_ajout = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True)

    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    tiktok = models.URLField(blank=True, null=True)

    type_partenaire = models.JSONField(default=list)

    date_deb = models.DateTimeField()
    date_fin = models.DateTimeField()

    liens_externes = models.JSONField(blank=True, null=True)
    date_creation_entreprise = models.DateField()

    priorite_affichage = models.IntegerField(null=True, blank=True)

    image_banniere = models.ImageField(upload_to='partenaire/partenaire_banniere/')

    # =========================
    # VALIDATION METIER
    # =========================
    def clean(self):

        if self.date_fin < self.date_deb:
            raise ValidationError("La date de fin doit être >= date de début.")


        validator = URLValidator()

        for k, v in (self.liens_externes or {}).items():
            try:
                validator(v)
            except:
                raise ValidationError(f"URL invalide: {v}")

    # =========================
    # SAVE LOGIC (RANKING SYSTEM)
    # =========================
    @transaction.atomic
    def save(self, *args, **kwargs):

        is_create = self._state.adding

        # =========================
        # ID GENERATION
        # =========================
        if is_create:
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                model_name='Partenaire'
            )
            counter.last_number += 1
            counter.save(update_fields=['last_number'])
            self.partenaire_id = f"PART{counter.last_number}"

        # =========================
        # PRIORITE LOGIC (SHIFT SYSTEM)
        # =========================

        if is_create:

            #  auto append
            if self.priorite_affichage is None:
                last = Partenaire.objects.aggregate(
                    max_p=Max("priorite_affichage")
                )["max_p"] or 0

                self.priorite_affichage = last + 1

            else:
                #  SHIFT INSERT
                Partenaire.objects.filter(
                    priorite_affichage__gte=self.priorite_affichage
                ).update(
                    priorite_affichage=F("priorite_affichage") + 1
                )

        else:
            #  UPDATE LOGIC
            old = Partenaire.objects.get(pk=self.pk)
            old_p = old.priorite_affichage
            new_p = self.priorite_affichage

            if new_p != old_p:

                if new_p < old_p:
                    Partenaire.objects.filter(
                        priorite_affichage__gte=new_p,
                        priorite_affichage__lt=old_p
                    ).update(
                        priorite_affichage=F("priorite_affichage") + 1
                    )

                elif new_p > old_p:
                    Partenaire.objects.filter(
                        priorite_affichage__gt=old_p,
                        priorite_affichage__lte=new_p
                    ).update(
                        priorite_affichage=F("priorite_affichage") - 1
                    )

        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_partenaire} ({self.partenaire_id})"