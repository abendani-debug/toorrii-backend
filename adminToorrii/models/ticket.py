from django.db import models, transaction
from django.utils import timezone
from adminToorrii.models.model_counter import ModelCounter  # compteur global


class Ticket(models.Model):
    class TypeTicket(models.TextChoices):
        RDV = "RDV", "Rendez-vous"
        FILE_D_ATTENTE = "FILE_D_ATTENTE", "File d'attente"

    class EtatTicket(models.TextChoices):
        EN_ATTENTE = "En_Attente", "En Attente"
        EN_COURS = "En_Cours", "En cours"
        UTILISER = "Utiliser", "Utilisé"
        ANNULER = "Annulé", "Annulé"
        EXPIRER = "Expirer", "Expiré"

    ticket_id = models.CharField(max_length=20, primary_key=True, editable=False)
    code_ticket = models.CharField(max_length=50, unique=True, editable=False,
                                   help_text="Code affiché au client (ex: CTK-20260225-0001)")

    client = models.ForeignKey("adminToorrii.Client", on_delete=models.PROTECT, related_name="tickets")
    file_attente = models.ForeignKey("adminToorrii.FileDattente", on_delete=models.PROTECT, related_name="tickets")
    rdv = models.OneToOneField("adminToorrii.RDV", on_delete=models.SET_NULL, related_name="ticket",
                               null=True, blank=True)

    type_ticket = models.CharField(max_length=20, choices=TypeTicket.choices)
    position = models.PositiveIntegerField(help_text="Position du ticket dans la file du jour", null=True, blank=True)
    creneau_prevue = models.DateTimeField(help_text="Créneau estimé de passage")
    est_actif_dans_file = models.BooleanField(default=True)
    etat_ticket = models.CharField(max_length=20, choices=EtatTicket.choices, default=EtatTicket.EN_ATTENTE)
    notifie = models.BooleanField(default=False)
    date_validation = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position"]
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        constraints = [
            models.UniqueConstraint(fields=["file_attente", "position"], name="unique_position_par_file")
        ]
        indexes = [
            models.Index(fields=["file_attente", "etat_ticket"]),
            models.Index(fields=["client"]),
            models.Index(fields=["creneau_prevue"]),
        ]

    # ==============================
    # LOGIQUE MÉTIER AUTOMATIQUE
    # ==============================

    def _generate_code_ticket(self):
        today = timezone.now().strftime("%Y%m%d")
        last_ticket_today = (
            Ticket.objects.select_for_update()
            .filter(code_ticket__startswith=f"CTK-{today}")
            .order_by("-code_ticket")
            .first()
        )
        if last_ticket_today:
            try:
                last_seq = int(last_ticket_today.code_ticket.split("-")[-1])
            except (IndexError, ValueError):
                last_seq = 0
            new_seq = last_seq + 1
        else:
            new_seq = 1
        return f"CTK-{today}-{new_seq:04d}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Génération atomique de ticket_id via ModelCounter
            if not self.ticket_id:
                counter, _ = ModelCounter.objects.select_for_update().get_or_create(model_name="Ticket")
                counter.last_number += 1
                self.ticket_id = f"TKT_{counter.last_number}"
                counter.save(update_fields=['last_number'])

            if not self.code_ticket:
                self.code_ticket = self._generate_code_ticket()

            # Synchronisation état → active
            self.est_actif_dans_file = self.etat_ticket not in [self.EtatTicket.ANNULER, self.EtatTicket.EXPIRER, self.EtatTicket.UTILISER]

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.file_attente.file_id} - Pos {self.position}"