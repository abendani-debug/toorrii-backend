from django.urls import path, include
from .views import AfficherProfileClientView, ModifierProfileClientView
from .views import ListeCategoriesView
from .views import ListeProfessionnelsParCategorieView, RechercherProfessionnelParWilayaView, AfficherDetailProfessionnelView
from .views import AfficherServicesView, AfficherServicesParProfessionnelView, AfficherDetailServiceView
from .views import ReserverRdvClientView, ModifierRdvClientView, AnnulerRdvClientView, AfficherHistoriqueRdvClientView, AfficherRdvsActifsClientView
from .views import DisponibilitesServiceView

urlpatterns = [
    path('profile/', AfficherProfileClientView.as_view(), name='client-profile'),
    path('profile/modifier', ModifierProfileClientView.as_view(), name='client-profile-modifier'),
    path('categories/', ListeCategoriesView.as_view(), name='categories'),
    path('categories/professionnels/<str:categorie_id>/', ListeProfessionnelsParCategorieView.as_view(), name='professionnel-par-categories'),
    path('professionnels/wilaya/', RechercherProfessionnelParWilayaView.as_view(), name='professionnel-par-wilaya'),
    path('professionnels/<str:professionnel_id>/', AfficherDetailProfessionnelView.as_view(), name='professionnel-detail'),
    path('services/', AfficherServicesView.as_view(), name='services'),
    path('services/professionnel/<str:professionnel_id>/', AfficherServicesParProfessionnelView.as_view(), name='services-par-professionnel'),
    path('services/detail/<str:service_id>/', AfficherDetailServiceView.as_view(), name='service-detail'),
    path('services/disponibilites/<str:service_id>/', DisponibilitesServiceView.as_view(), name='service-disponibilites'),

#RDV
    path('rdv/reserver/<str:service_id>/', ReserverRdvClientView.as_view(), name='reserver-rdv'),
    path('rdv/modifier/', ModifierRdvClientView.as_view(), name='modifier-rdv'),
    path('rdv/annuler/<str:rdv_id>/', AnnulerRdvClientView.as_view(), name='annuler-rdv'),
    path('rdv/historique/', AfficherHistoriqueRdvClientView.as_view(), name='historique-rdv'),
    path('rdv/actifs/', AfficherRdvsActifsClientView.as_view(), name='rdvs-actifs'),
]