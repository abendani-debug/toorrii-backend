from django.urls import path
from adminToorrii.views import AjouterContacteView, ModifierContacteView
from adminToorrii.views import AjouterPartenaireView, ModifierPartenaireView, SupprimerPartenaireView
from adminToorrii.views import AjouterAboutNousView, ModifierAboutNousView
from adminToorrii.views import AjouterPolitiqueView, ModifierPolitiqueView
from adminToorrii.views import AjouterConditionDutilisationView, ModifierConditionDutilisationView
from adminToorrii.views import AfficherAdminCompteView, ModifierAdminCompteView
from adminToorrii.views import AfficherCategoriesView, AjouterCategorieView, ModifierCategorieView, SuspendreCategorieView, SupprimerCategorieView
from adminToorrii.views import AfficherProfessionnelView, ProfessionnelDetailView, AjouterProfessionnelView, SupprimerProfessionnelView, ModifierProfessionnelView, ActiverProfessionnelView, DesactiverProfessionnelView
from adminToorrii.views.serviceViews import AfficherServiceProfessionnelView, AjouterServiceView, AfficherServiceDetailView, ModifierServiceView, SuspendreServiceView, SupprimerServiceView
from adminToorrii.views.clientViews import AfficherClientView
from adminToorrii.views.statistiquesViews import NombreClientView, RDVStatsParServiceView, RDVStatsParDateGlobalView, RDVStatsParHeureView, RDVStatsParJourSemaineView, RDVStatsParMoisView, RDVStatsParAnneeView, RDVStatsParIntervalleView, RDVNombreAbsentView, RDVNombreAbsentParServiceView, RDVNombrePresentView, RDVNombrePresentParServiceView, FileDattenteStatistiquesView, FileDattenteStatsParDateView, FileDattenteStatsParHeureView, FileDattenteStatsParJourView, FileDattenteStatsParMoisView, FileDattenteStatsParAnneeView, FileDattenteStatsParIntervalleView, NombreTotalProfessionnelsView, NombreTotalProfessionnelsSuspendusView, NombreTotalProfessionnelsSupprimesView, NombreTotalProfessionnelsActivesView, NombreServicesParProView, NombreTotalCategoriesView, NombreTotalCategoriesProView, NombreTotalCategoriesServicesView, NombreTotalRdvView, NombreTotalServicesView
from adminToorrii.views.fileDattenteViews import AfficherFileDattenteDetailView, AfficherFileDattenteView, AfficherFilesDattenteParProfessionnelView, AfficherListeFileDattenteView, AfficherDetailFileAttenteClientView
from adminToorrii.views.rdvViews import AfficherRdvParProfessionnelView, AjouterRdvView, SupprimerRdvView, AfficherListeReservationsClientsView, AfficherDetailReservationView, ModifierRdvView
from adminToorrii.views.planningViews import AfficherPlanningMoisView, AfficherCreneauxView
from adminToorrii.views.categorieViews import AfficherCategoriesDetailView, AfficherEnfantsCategorieView
urlpatterns = [
    path("contacte/ajouter/", AjouterContacteView.as_view(), name="contacte-ajouter"),
    path("contacte/modifier/", ModifierContacteView.as_view(), name="contacte-modifier"),
    path("partenaire/ajouter/", AjouterPartenaireView.as_view(), name="partenaire-ajouter"),
    path('partenaire/modifier/<str:partenaire_id>/', ModifierPartenaireView.as_view(), name='partenaire-modifier'),
    path('partenaire/supprimer/<str:partenaire_id>/', SupprimerPartenaireView.as_view(), name='partenaire-supprimer'),
    path("AboutNous/ajouter/", AjouterAboutNousView.as_view(), name="aboutnous-ajouter"),
    path("AboutNous/modifier/<str:about_id>/", ModifierAboutNousView.as_view(), name="aboutnous-modifier"),
    path("politique_confidentialite/ajouter/", AjouterPolitiqueView.as_view(), name="politique-confidentialite-ajouter"),   
    path("politique_confidentialite/modifier/<str:politique_id>/", ModifierPolitiqueView.as_view(), name="politique-confidentialite-modifier"),
    path("condition_dutilisation/ajouter/", AjouterConditionDutilisationView.as_view(), name="condition-dutilisation-ajouter"),
    path("condition_dutilisation/modifier/<str:condition_id>/", ModifierConditionDutilisationView.as_view(), name="condition-dutilisation-modifier"),
    path("compte/afficher/", AfficherAdminCompteView.as_view(), name="afficher-admin-compte"),
    path("compte/modifier/", ModifierAdminCompteView.as_view(), name="modifier-admin-compte"),
    path("categories/afficher/", AfficherCategoriesView.as_view(), name="afficher-categories"),
    path("categories/ajouter/", AjouterCategorieView.as_view(), name="ajouter-categorie"),
    path("categories/modifier/<str:categorie_id>/", ModifierCategorieView.as_view(), name="modifier-categorie"),
    path("categories/suspendre/<str:categorie_id>/", SuspendreCategorieView.as_view(), name="suspendre-categorie"),
    path("categories/supprimer/<str:categorie_id>/", SupprimerCategorieView.as_view(), name="supprimer-categorie"),
    path("categories/afficher/<str:categorie_id>/", AfficherCategoriesDetailView.as_view(), name="afficher-categorie"),
    path("categories/<str:parent_id>/enfants/", AfficherEnfantsCategorieView.as_view(), name="afficher-enfants-categorie"),
    path("professionnels/afficher/", AfficherProfessionnelView.as_view(), name="afficher-professionnels"),
    path("professionnels/afficher/<str:professionnel_id>/", ProfessionnelDetailView.as_view(), name="afficher-professionnel-detail"),
    path("professionnels/ajouter/", AjouterProfessionnelView.as_view(), name="ajouter-professionnel"),
    path("professionnels/supprimer/<str:professionnel_id>/", SupprimerProfessionnelView.as_view(), name="supprimer-professionnel"),
    path("professionnels/modifier/<str:professionnel_id>/", ModifierProfessionnelView.as_view(), name="modifier-professionnel"),
    path("professionnels/activer/<str:professionnel_id>/", ActiverProfessionnelView.as_view(), name="activer-professionnel"),
    path("professionnels/desactiver/<str:professionnel_id>/", DesactiverProfessionnelView.as_view(), name="desactiver-professionnel"),
    path("services/afficher/<str:professionnel_id>/", AfficherServiceProfessionnelView.as_view(), name="afficher-services-professionnel"),
    path("services/ajouter/<str:professionnel_id>/", AjouterServiceView.as_view(), name="ajouter-service"),
    path("services/afficher_detail/<str:service_id>/", AfficherServiceDetailView.as_view(), name="afficher-service-detail"),
    path("services/modifier/<str:service_id>/", ModifierServiceView.as_view(), name="modifier-service"),
    path("services/suspendre/<str:service_id>/", SuspendreServiceView.as_view(), name="suspendre-service"),
    path("services/supprimer/<str:service_id>/", SupprimerServiceView.as_view(), name="supprimer-service"),
    path("client/afficher/",AfficherClientView.as_view(), name="afficher-clients"),
    path("statistiques/nombre_clients/",NombreClientView.as_view(), name="nombre-clients"),
    path("statistiques/rdv/<str:service_id>/",RDVStatsParServiceView.as_view(), name="nombre-rdvs-service"), #afficher statistiques des rdv par service 
    path("statistiques/rdvs/date/",RDVStatsParDateGlobalView.as_view(), name="rdv-date"), #afficher statistiques par date précise
    path("statistiques/rdvs/heure/",RDVStatsParHeureView.as_view(), name="rdv-heure"), #afficher statistiques de tous les heures d`une date précise
    path("statistiques/rdvs/jour/",RDVStatsParJourSemaineView.as_view(), name="rdv-jour"),#rdv/statistiques/jour/?jour=lundi
    path("statistiques/rdvs/mois/",RDVStatsParMoisView.as_view(), name="rdv-mois"),#rdv/statistiques/mois/?mois=mars
    path("statistiques/rdvs/annee/",RDVStatsParAnneeView.as_view(), name="rdv-annee"),#rdv/statistiques/annee/?annee=2026
    path("statistiques/rdvs/intervalle/",RDVStatsParIntervalleView.as_view(), name="rdv-intervalle"),#/rdv/statistiques/intervalle/?date_debut=2026-01-01&date_fin=2026-01-31
    path("statistiques/rdvs/absent/",RDVNombreAbsentView.as_view(), name="rdv-absent"),#/rdv/statistiques/absent/?date_debut=2026-01-01&date_fin=2026-01-31  
    path("statistiques/rdvs/present/",RDVNombrePresentView.as_view(), name="rdv-present"),
    path("statistiques/rdvs/absent/service/<str:service_id>/",RDVNombreAbsentParServiceView.as_view(), name="rdv-absent-service"),
    path("statistiques/rdvs/present/service/<str:service_id>/",RDVNombrePresentParServiceView.as_view(), name="rdv-present-service"),
    path("statistiques/file_dattente/",FileDattenteStatistiquesView.as_view(), name="file_dattente-stats"),#statistiques/file_dattente/?date=2026-03-05
    path("statistiques/file_dattente/date/",FileDattenteStatsParDateView.as_view(), name="file_dattente-stats-date"),#statistiques/file_dattente/date/?date=2026-03-05
    path("statistiques/file_dattente/heure/",FileDattenteStatsParHeureView.as_view(), name="file_dattente-stats-heure"),#statistiques/file_dattente/date/?date=2026-03-05 & heure = 13
    path("statistiques/file_dattente/jour/",FileDattenteStatsParJourView.as_view(), name="file_dattente-stats-jour"),#statistiques/file_dattente/?jour=dimanche
    path("statistiques/file_dattente/mois/",FileDattenteStatsParMoisView.as_view(), name="file_dattente-stats-mois"),#statistiques/file_dattente/?mois=1
    path("statistiques/file_dattente/annee/",FileDattenteStatsParAnneeView.as_view(), name="file_dattente-stats-annee"),#statistiques/file_dattente/?annee=2012
    path("statistiques/file_dattente/intervalle/",FileDattenteStatsParIntervalleView.as_view(), name="file_dattente-stats-intervalle"),#statistiques/file_dattente/?date_debut=YYYY-MM-DD&date_fin=YYYY-MM-DD
    path("statistiques/nombre_professionnels/",NombreTotalProfessionnelsView.as_view(), name="nombre-professionnels"),
    path("statistiques/nombre_professionnels/suspendus",NombreTotalProfessionnelsSuspendusView.as_view(), name="nombre-professionnels-suspendus"),
    path("statistiques/nombre_professionnels/supprimes",NombreTotalProfessionnelsSupprimesView.as_view(), name="nombre-professionnels-supprimes"),
    path("statistiques/nombre_professionnels/actives",NombreTotalProfessionnelsActivesView.as_view(), name="nombre-professionnels-actives"),
    path("statistiques/professionnels/services/<str:professionnel_id>/",NombreServicesParProView.as_view(), name="nombre-professionnels-services"),
    path("statistiques/nombre_categories/",NombreTotalCategoriesView.as_view(), name="nombre-categories"),
    path("statistiques/nombre_categories/professionnel/",NombreTotalCategoriesProView.as_view(), name="nombre-categories-professionnel"),
    path("statistiques/nombre_categories/service/",NombreTotalCategoriesServicesView.as_view(), name="nombre-categories-service"),
    path("statistiques/Professionnel/Services/NbrDeServices/",NombreTotalServicesView.as_view(), name="nombre-services-services"),
    path("statistiques/nombre_rdvs/",NombreTotalRdvView.as_view(), name="nombre-rdvs-services"),
    path("files/afficher/detail/<str:file_id>/", AfficherFileDattenteDetailView.as_view(), name="afficher-file_dattente-detail"),
    path("files/afficher/<str:service_id>/", AfficherFileDattenteView.as_view(), name="afficher-file_dattente"),
    path("files/afficher/", AfficherListeFileDattenteView.as_view(), name="afficher-file_dattente"),
    path("files/afficher/professionnel/<str:professionnel_id>/", AfficherFilesDattenteParProfessionnelView.as_view(), name="afficher-file_dattente-pro"),
    path("files/afficher/detail/client/<str:client_id>/", AfficherDetailFileAttenteClientView.as_view(), name="afficher-file_dattente-client"),
    path("rdvs/afficher/professionnel/<str:professionnel_id>/", AfficherRdvParProfessionnelView.as_view(), name="afficher-rdvs-pro"),
    path("rdvs/ajouter/<str:service_id>/", AjouterRdvView.as_view(), name="ajouter-rdvs"),
    path("rdvs/modifier/<str:rdv_id>/", ModifierRdvView.as_view(), name="modifier-rdvs"),
    path("rdvs/supprimer/<str:rdv_id>/", SupprimerRdvView.as_view(), name="supprimer-rdvs"),
    path("rdvs/afficher/reservations", AfficherListeReservationsClientsView.as_view(), name="afficher-reservations"),
    path("rdvs/afficher/reservation/detail/<str:rdv_id>/", AfficherDetailReservationView.as_view(), name="afficher-reservation-detail"),
    path("planning/mois/afficher/<str:service_id>/", AfficherPlanningMoisView.as_view(), name="planning-mois-afficher"),#planning/mois/afficher/SER_1/?year=2026&month=3
    path("planning/creneaux/afficher/<str:service_id>/", AfficherCreneauxView.as_view(), name="planning-creneaux-afficher"),#planning/creneaux/afficher/SER_1/?date=2026-03-05
    
]  
