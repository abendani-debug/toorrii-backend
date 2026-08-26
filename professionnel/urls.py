from django.urls import path, include
from .views import AjouterServiceView, ModifierServiceView, SupprimerServiceView, AfficherServiceView, AfficherServiceDetailView
from .views import ProfessionnelModifierCompteView, ProfessionnelDetailCompteView, ProfessionnelDemandeDesactivationCompteView
from .views import  AfficherCreneauxView, AfficherPlanningMoisView
from .views import AjouterRdvView, ModifierRdvView, SupprimerRdvView, MarquerTerminerRdvProView, MarquerAbsentRdvProView, ValiderRdvView, AnnulerRdvView, AfficherDetailRdvView, ListRdvProView, ListRdvParServiceProView
from .views import AfficherFileDattenteView, AfficherFileDattenteDetailView, AjouterClientFileAttenteView, ModifierPositionClientFileView, SupprimerClientFileAttenteView, TerminerClientFileAttenteView
from .views import ProNombreTotalRDVView, ProNombreRDVParServiceView, ProRDVParDateView, ProRDVParJourView, ProRDVParMoisView, ProRDVParAnneeView, ProRDVParIntervalleView, ProRDVNombreAbsentView, ProRDVNombrePresentView, ProRDVNombrePresentParServiceView
from .views import FileDattenteStatsParMoisView, ProFileAttenteStatsParAnneeView, ProFileAttenteStatsIntervalleView, ProTauxMoyenClientsParServiceView
from .views import AfficherCategoriesView
urlpatterns = [
#Compte Professionnel    
    path("compte/modifier/", ProfessionnelModifierCompteView.as_view(), name="modifier-compte"),
    path("compte/detail/", ProfessionnelDetailCompteView.as_view(), name="detail-compte"),
    path("compte/demande/desactivation/", ProfessionnelDemandeDesactivationCompteView.as_view(), name="demande-desactivation-compte"),
#Service    
    path("services/ajouter/", AjouterServiceView.as_view(), name="ajouter-service"),
    path("services/modifier/<str:service_id>/", ModifierServiceView.as_view(), name="modifier-service"),
    path("services/supprimer/<str:service_id>/", SupprimerServiceView.as_view(), name="supprimer-service"),
    path("services/afficher/", AfficherServiceView.as_view(), name="afficher-service"),
    path("services/afficher/<str:service_id>/", AfficherServiceDetailView.as_view(), name="afficher-service-detail"),
#Planning
    path("planning/mois/afficher/<str:service_id>/", AfficherPlanningMoisView.as_view(), name="planning-mois-afficher"),#planning/mois/afficher/SER_1/?year=2026&month=3
    path("planning/creneaux/afficher/<str:service_id>/", AfficherCreneauxView.as_view(), name="planning-creneaux-afficher"),#planning/creneaux/afficher/SER_1/?date=2026-03-05
#RDV
    path("rdvs/ajouter/<str:service_id>/", AjouterRdvView.as_view(), name="ajouter-rdvs"),
    path("rdvs/modifier/<str:rdv_id>/", ModifierRdvView.as_view(), name="modifier-rdvs"),
    path("rdvs/supprimer/<str:rdv_id>/", SupprimerRdvView.as_view(), name="supprimer-rdvs"),
    path("rdvs/Terminer/<str:rdv_id>/", MarquerTerminerRdvProView.as_view(), name="terminer-rdvs"),
    path("rdvs/Absent/<str:rdv_id>/", MarquerAbsentRdvProView.as_view(), name="absent-rdvs"),
    path("rdvs/Valider/<str:rdv_id>/", ValiderRdvView.as_view(), name="valider-rdvs"),
    path("rdvs/Annuler/<str:rdv_id>/", AnnulerRdvView.as_view(), name="annuler-rdvs"),
    path("rdvs/Afficher/detail/<str:rdv_id>/", AfficherDetailRdvView.as_view(), name="afficher-rdvs-detail"),
    path("rdvs/Afficher/", ListRdvProView.as_view(), name="afficher-rdvs"),
    path("rdvs/Afficher/service/<str:service_id>/", ListRdvParServiceProView.as_view(), name="afficher-rdvs-service"),
    
#FileDattente
    path("files/afficher/<str:service_id>/", AfficherFileDattenteView.as_view(), name="afficher-file-service-date"),
    path("files/afficher/detail/<str:file_id>/", AfficherFileDattenteDetailView.as_view(), name="afficher-file-detail"),
    path("files/ajouter/<str:service_id>/", AjouterClientFileAttenteView.as_view(), name="ajouter-file"),
    path("files/modifier/client/position/<str:service_id>/<str:ticket_id>/", ModifierPositionClientFileView.as_view(), name="modifier-postion-client"),
    path("files/supprimer/<str:service_id>/<str:ticket_id>/", SupprimerClientFileAttenteView.as_view(), name="supprimer-file"),
    path("files/terminer/client/<str:service_id>/<str:ticket_id>/", TerminerClientFileAttenteView.as_view(), name="terminer-client-file"),

#Statistiques
    path("statistiques/nombre_rdvs/",ProNombreTotalRDVView.as_view(), name="nombre-rdvs-pro"),
    path("statistiques/rdv/<str:service_id>/",ProNombreRDVParServiceView.as_view(), name="nombre-rdvs-service"), #afficher statistiques des rdv par service
    path("statistiques/rdvs/date/",ProRDVParDateView.as_view(), name="rdv-date"), #afficher statistiques par date précise
    path("statistiques/rdvs/jour/",ProRDVParJourView.as_view(), name="rdv-jour"),#rdv/statistiques/jour/?jour=lundi
    path("statistiques/rdvs/mois/",ProRDVParMoisView.as_view(), name="rdv-mois"),#rdv/statistiques/mois/?mois=mars
    path("statistiques/rdvs/annee/",ProRDVParAnneeView.as_view(), name="rdv-annee"),#rdv/statistiques/annee/?annee=2026
    path("statistiques/rdvs/intervalle/",ProRDVParIntervalleView.as_view(), name="rdv-intervalle"),#/rdv/statistiques/intervalle/?date_debut=2026-01-01&date_fin=2026-01-31
    path("statistiques/rdvs/absent/",ProRDVNombreAbsentView.as_view(), name="rdv-absent"),#/rdv/statistiques/absent/?date_debut=2026-01-01&date_fin=2026-01-31
    path("statistiques/rdvs/absent/service/<str:service_id>/",ProRDVNombreAbsentView.as_view(), name="rdv-absent-service"),
    path("statistiques/rdvs/present/",ProRDVNombrePresentView.as_view(), name="rdv-present"),
    path("statistiques/rdvs/present/service/<str:service_id>/",ProRDVNombrePresentParServiceView.as_view(), name="rdv-present-service"),
    path("statistiques/file_dattente/mois/",FileDattenteStatsParMoisView.as_view(), name="file_dattente-stats-mois"),#statistiques/file_dattente/?mois=1
    path("statistiques/file_dattente/annee/",ProFileAttenteStatsParAnneeView.as_view(), name="file_dattente-stats-annee"),#statistiques/file_dattente/?annee=2012
    path("statistiques/file_dattente/intervalle/",ProFileAttenteStatsIntervalleView.as_view(), name="file_dattente-stats-intervalle"),#statistiques/file_dattente/?date_debut=YYYY-MM-DD&date_fin=YYYY-MM-DD
    path("statistiques/file_dattente/taux/mayen",ProTauxMoyenClientsParServiceView.as_view(), name="file_dattente-taux-moyen"),

#Catégories
    path("categories/afficher/", AfficherCategoriesView.as_view(), name="afficher-categories"),    
]