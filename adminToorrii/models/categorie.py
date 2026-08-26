from django.db import models, transaction
from django.utils import timezone
from django.db.models import F
from .model_counter import ModelCounter


class Categorie(models.Model):
    categorie_id = models.CharField(max_length=20, primary_key=True, editable=False)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='enfants'
    )
    niveau = models.PositiveSmallIntegerField(default=1, editable=False)

    nom_categorie = models.JSONField(default=dict)
    description_categorie = models.JSONField(default=dict)

    active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)

    photo_principale_cat = models.ImageField(
        upload_to='categorie/photo_principale',
        blank=True,
        null=True
    )

    couleur_theme = models.CharField(max_length=50, blank=True, default='')
    ordre_affichage = models.PositiveIntegerField()

    class Meta:
        ordering = ["ordre_affichage"]

    @transaction.atomic
    def save(self, *args, **kwargs):

        is_create = self._state.adding

        # =========================
        #  ID GENERATION
        # =========================
        if is_create:
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                model_name='Categorie'
            )
            counter.last_number += 1
            counter.save(update_fields=['last_number'])
            self.categorie_id = f"Cat_{counter.last_number}"

        # =========================
        #  NIVEAU AUTO-CALCUL
        # =========================
        if self.parent:
            self.niveau = self.parent.niveau + 1
        else:
            self.niveau = 1

        # =========================
        #  CREATE LOGIC (SHIFT INSERT — frères seulement)
        # =========================
        if is_create:

            siblings = Categorie.objects.filter(parent=self.parent)

            if not self.ordre_affichage:
                last = siblings.aggregate(
                    max_order=models.Max("ordre_affichage")
                )["max_order"] or 0
                self.ordre_affichage = last + 1

            else:
                siblings.filter(
                    ordre_affichage__gte=self.ordre_affichage
                ).update(
                    ordre_affichage=F("ordre_affichage") + 1
                )

        # =========================
        #  UPDATE LOGIC (SHIFT MOVE — frères seulement)
        # =========================
        else:
            old = Categorie.objects.get(pk=self.pk)
            old_order = old.ordre_affichage
            new_order = self.ordre_affichage

            if new_order != old_order:
                siblings = Categorie.objects.filter(parent=self.parent).exclude(pk=self.pk)

                if new_order < old_order:
                    siblings.filter(
                        ordre_affichage__gte=new_order,
                        ordre_affichage__lt=old_order
                    ).update(
                        ordre_affichage=F("ordre_affichage") + 1
                    )

                elif new_order > old_order:
                    siblings.filter(
                        ordre_affichage__gt=old_order,
                        ordre_affichage__lte=new_order
                    ).update(
                        ordre_affichage=F("ordre_affichage") - 1
                    )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_categorie} (niveau {self.niveau} — {self.categorie_id})"
