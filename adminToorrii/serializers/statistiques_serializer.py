from rest_framework import serializers

class RDVStatsServiceSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    service_nom = serializers.CharField()
    total_rdv = serializers.IntegerField()
    rdv_par_statut = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Nombre de RDV pour chaque statut pour ce service"
    )





class RDVStatsParDateGlobalSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_rdv = serializers.IntegerField()
    rdv_par_statut = serializers.DictField(child=serializers.IntegerField())
    rdv_par_mode_reservation = serializers.DictField(child=serializers.IntegerField())
    rdv_par_source_creation = serializers.DictField(child=serializers.IntegerField())


class HeureStatsSerializer(serializers.Serializer):
    heure = serializers.CharField()
    total = serializers.IntegerField()
    confirmes = serializers.IntegerField()
    en_attente = serializers.IntegerField()
    annules = serializers.IntegerField()
    terminer = serializers.IntegerField()   
    absent = serializers.IntegerField()     


class RDVStatsParHeureSerializer(serializers.Serializer):
    stats_par_heure = HeureStatsSerializer(many=True)  




class NombreTotalRDVSerializer(serializers.Serializer):
    total_rdvs = serializers.IntegerField()


class StatutSerializer(serializers.Serializer):
    En_attente = serializers.IntegerField()
    Confirmer = serializers.IntegerField()
    Annuler = serializers.IntegerField()
    Absent = serializers.IntegerField()
    Terminer = serializers.IntegerField()


class ModeReservationSerializer(serializers.Serializer):
    RDV = serializers.IntegerField()
    File_attente = serializers.IntegerField()


class SourceCreationSerializer(serializers.Serializer):
    Admin = serializers.IntegerField()
    Client = serializers.IntegerField()


class RDVStatsParMoisSerializer(serializers.Serializer):
    mois = serializers.CharField()
    mois_numero = serializers.IntegerField()
    total_rdv = serializers.IntegerField()

    rdv_par_statut = StatutSerializer()
    rdv_par_mode_reservation = ModeReservationSerializer()
    rdv_par_source_creation = SourceCreationSerializer()

class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()



class RDVParStatutSerializer(serializers.Serializer):
    En_attente = serializers.IntegerField()
    Confirmer = serializers.IntegerField()
    Annuler = serializers.IntegerField()
    Absent = serializers.IntegerField()
    Terminer = serializers.IntegerField()

class RDVParModeSerializer(serializers.Serializer):
    En_ligne = serializers.IntegerField(required=False)
    Sur_place = serializers.IntegerField(required=False)

class RDVParSourceSerializer(serializers.Serializer):
    Client = serializers.IntegerField(required=False)
    Pro = serializers.IntegerField(required=False)
    Admin = serializers.IntegerField(required=False)

class RDVStatsParAnneeSerializer(serializers.Serializer):
    annee = serializers.IntegerField()
    total_rdv = serializers.IntegerField()

    rdv_par_statut = RDVParStatutSerializer()
    rdv_par_mode_reservation = RDVParModeSerializer()
    rdv_par_source_creation = RDVParSourceSerializer()
    
class RDVStatsParDateGlobalSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_rdv = serializers.IntegerField()

    rdv_par_statut = RDVParStatutSerializer()
    rdv_par_mode_reservation = RDVParModeSerializer()
    rdv_par_source_creation = RDVParSourceSerializer()

class RDVStatsParIntervalleSerializer(serializers.Serializer):
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()
    total_rdv = serializers.IntegerField()

    rdv_par_statut = RDVParStatutSerializer()
    rdv_par_mode_reservation = RDVParModeSerializer()
    rdv_par_source_creation = RDVParSourceSerializer()

class RDVNombreAbsentSerializer(serializers.Serializer):
    nombre_clients_absents = serializers.IntegerField()


class RDVNombreAbsentParServiceSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    service_nom = serializers.CharField()
    nombre_clients_absents = serializers.IntegerField()

class RDVParModeReservationSerializer(serializers.Serializer):
    RDV = serializers.IntegerField()
    File_attente = serializers.IntegerField()


class RDVParSourceCreationSerializer(serializers.Serializer):
    Admin = serializers.IntegerField()
    Client = serializers.IntegerField()


class RDVStatsParJourResponseSerializer(serializers.Serializer):
    jour = serializers.CharField()
    total_rdv = serializers.IntegerField()

    rdv_par_statut = RDVParStatutSerializer()
    rdv_par_mode_reservation = RDVParModeReservationSerializer()
    rdv_par_source_creation = RDVParSourceCreationSerializer()



class RDVNombrePresentSerializer(serializers.Serializer):
    nombre_clients_presents = serializers.IntegerField()


class RDVNombrePresentParServiceSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    service_nom = serializers.CharField()
    nombre_clients_presents = serializers.IntegerField()


class FileDattenteStatistiquesSerializer(serializers.Serializer):
    total_files = serializers.IntegerField()
    files_en_cours = serializers.IntegerField()
    files_terminees = serializers.IntegerField()
    files_suspendues = serializers.IntegerField()
    total_clients_dans_files = serializers.IntegerField()
    temps_moyen_attente_global = serializers.FloatField()

class FileDattenteStatsParAnneeSerializer(serializers.Serializer):
    annee = serializers.IntegerField()

    total_files = serializers.IntegerField()
    files_en_cours = serializers.IntegerField()
    files_terminees = serializers.IntegerField()
    files_suspendues = serializers.IntegerField()
    temps_moyen_attente = serializers.FloatField()
    total_clients_dans_files = serializers.IntegerField()


class FileDattenteStatsParDateSerializer(serializers.Serializer):
    date = serializers.DateField()

    total_files = serializers.IntegerField()
    files_en_cours = serializers.IntegerField()
    files_terminees = serializers.IntegerField()
    files_suspendues = serializers.IntegerField()

    total_clients_dans_files = serializers.IntegerField()

    temps_moyen_attente_global = serializers.FloatField()



class FileDattenteStatsParHeureSerializer(serializers.Serializer):
    heure = serializers.IntegerField()

    stats_exactes = FileDattenteStatistiquesSerializer()

class NombreTotalServicesSerializer(serializers.Serializer):
    total_services = serializers.IntegerField()



class NombreTotalCategoriesSerializer(serializers.Serializer):
    total_categories = serializers.IntegerField()




class NombreServicesParCategorieSerializer(serializers.Serializer):
    categorie_id = serializers.CharField()
    categorie_nom = serializers.CharField()
    total_services = serializers.IntegerField()

class NombreProfessionnelsParCategorieSerializer(serializers.Serializer):
    categorie_id = serializers.CharField()
    categorie_nom = serializers.CharField()
    total_professionnels = serializers.IntegerField()


class NombreClientsSerializer(serializers.Serializer):
    total_clients = serializers.IntegerField()
    clients_actifs = serializers.IntegerField()
    clients_inactifs = serializers.IntegerField()


class NombreTotalProfessionnelsSerializer(serializers.Serializer):
    total_professionnels = serializers.IntegerField()


class NombreProfessionnelsActifsSerializer(serializers.Serializer):
    total_professionnels_actifs = serializers.IntegerField()


class NombreProfessionnelsSupprimesSerializer(serializers.Serializer):
    total_professionnels_supprimes = serializers.IntegerField()


class NombreProfessionnelsSuspendusSerializer(serializers.Serializer):
    total_professionnels_suspendus = serializers.IntegerField()



class NombreServicesParProfessionnelSerializer(serializers.Serializer):
    professionnel_id = serializers.CharField()
    total_services = serializers.IntegerField()