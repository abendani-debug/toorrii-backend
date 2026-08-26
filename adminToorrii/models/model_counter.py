from django.db import models, transaction
from django.utils import timezone

# Modèle de compteur générique pour gérer tous les IDs
class ModelCounter(models.Model):
    """
    Modèle pour garder le compteur de chaque modèle avec préfixe.
    Exemple: 'AboutNous' -> about1, about2...
    """
    model_name = models.CharField(max_length=50, unique=True)
    last_number = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.model_name} - {self.last_number}"