from django.db import models
from django.utils import timezone
from adminToorrii.models.model_counter import ModelCounter


class ProfessionnelLead(models.Model):
    """
    Professionnel référencé automatiquement (scraping Google Places).
    N'a pas encore de compte Toorrii — utilisé pour le démarchage.
    """

    class StatutLead(models.TextChoices):
        NON_CONTACTE = 'non_contacte', 'Non contacté'
        CONTACTE     = 'contacte',     'Contacté'
        INTERESSE    = 'interesse',    'Intéressé'
        INSCRIT      = 'inscrit',      'Inscrit sur Toorrii'
        REFUSE       = 'refuse',       'Refusé'

    lead_id = models.CharField(max_length=20, primary_key=True, editable=False)

    # ── Données Google Places ─────────────────────────────────────────────────
    place_id    = models.CharField(max_length=255, unique=True)
    nom         = models.CharField(max_length=255)
    specialite  = models.CharField(max_length=100)          # ex : "Cardiologue"
    categorie   = models.ForeignKey(
        'adminToorrii.Categorie',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='leads'
    )

    # ── Coordonnées ───────────────────────────────────────────────────────────
    telephone   = models.CharField(max_length=30, blank=True, default='')
    adresse     = models.TextField(blank=True, default='')
    wilaya      = models.CharField(max_length=100, default='Oran')
    latitude    = models.FloatField(null=True, blank=True)
    longitude   = models.FloatField(null=True, blank=True)

    # ── CRM ───────────────────────────────────────────────────────────────────
    statut      = models.CharField(
        max_length=20,
        choices=StatutLead.choices,
        default=StatutLead.NON_CONTACTE
    )
    note        = models.TextField(blank=True, default='')

    # ── Métadonnées ───────────────────────────────────────────────────────────
    source           = models.CharField(max_length=50, default='google_places')
    date_ajout       = models.DateTimeField(default=timezone.now)
    date_modification= models.DateTimeField(auto_now=True)

    # ── Conversion : quand le lead s'inscrit, on lie son compte ───────────────
    professionnel = models.OneToOneField(
        'adminToorrii.Professionnel',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='lead_origine'
    )

    class Meta:
        verbose_name        = "Lead Professionnel"
        verbose_name_plural = "Leads Professionnels"
        ordering            = ['-date_ajout']
        indexes = [
            models.Index(fields=['wilaya']),
            models.Index(fields=['statut']),
            models.Index(fields=['wilaya', 'statut']),
        ]

    def __str__(self):
        return f"{self.nom} — {self.specialite} ({self.wilaya})"

    def save(self, *args, **kwargs):
        if not self.lead_id:
            counter, _ = ModelCounter.objects.select_for_update().get_or_create(
                model_name="ProfessionnelLead"
            )
            counter.last_number += 1
            self.lead_id = f"LEAD_{counter.last_number}"
            counter.save(update_fields=['last_number'])
        super().save(*args, **kwargs)
