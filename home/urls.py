from django.urls import path
from home.views import AfficherContacteView, AfficherAboutNousView, AfficherPolitiqueView, AfficherConditionDutilisationView, AfficherPartenaireView, AfficherPartenaireDetailView, AfficherAboutNousDetailView, AfficherConditionDutilisationDetailView, AfficherPolitiqueDetailView



urlpatterns = [
    path("contacte/", AfficherContacteView.as_view(), name="contacte-afficher"),
    path("AboutNous/", AfficherAboutNousView.as_view(), name="aboutnous-afficher-detail"),
    path("AboutNous/<str:about_id>", AfficherAboutNousDetailView.as_view(), name="aboutnous-afficher"),
    path("politique_confidentialite/", AfficherPolitiqueView.as_view(), name="politique-confidentialite-afficher"),
    path("politique_confidentialite/<str:politique_id>", AfficherPolitiqueDetailView.as_view(), name="politique-confidentialite-afficher-detail"),
    path("condition_dutilisation/", AfficherConditionDutilisationView.as_view(), name="condition-dutilisation-afficher"),
    path("condition_dutilisation/<str:condition_id>", AfficherConditionDutilisationDetailView.as_view(), name="condition-dutilisation-afficher-detail"),
    path("partenaire/", AfficherPartenaireView.as_view(), name="partenaire-afficher"),
    path("partenaire/<str:partenaire_id>", AfficherPartenaireDetailView.as_view(), name="partenaire-afficher-detail"),
]
