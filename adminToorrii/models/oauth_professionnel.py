from django.db import models
from django.utils import timezone

class OAuthProfessionnel(models.Model):
    email = models.EmailField(unique=True)
    date_creation = models.DateTimeField(default=timezone.now)
    profil_complet = models.BooleanField(default=False)
    utilisateur = models.OneToOneField(
        'adminToorrii.Utilisateur',
        on_delete=models.CASCADE,
        related_name="oauth_professionnel_profile"
    )

    def __str__(self):
        return self.email