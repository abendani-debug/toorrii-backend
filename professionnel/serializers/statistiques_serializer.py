from rest_framework import serializers


class ProRDVTotalSerializer(serializers.Serializer):
    total_rdv = serializers.IntegerField()


class ProRDVParServiceItemSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    service_nom = serializers.CharField()
    total_rdv = serializers.IntegerField()


class ProRDVParServiceSerializer(serializers.Serializer):
    services = ProRDVParServiceItemSerializer(many=True)

class ProRDVParDateSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_rdv = serializers.IntegerField()

class ProRDVParJourSerializer(serializers.Serializer):
    date = serializers.DateField()
    total_rdv = serializers.IntegerField()
    rdv_par_statut = serializers.DictField(child=serializers.IntegerField())


class ProRDVParMoisSerializer(serializers.Serializer):
    mois = serializers.IntegerField()
    annee = serializers.IntegerField()
    total_rdv = serializers.IntegerField()
    rdv_par_statut = serializers.DictField(child=serializers.IntegerField())


class ProRDVParAnneeSerializer(serializers.Serializer):
    annee = serializers.IntegerField()
    total_rdv = serializers.IntegerField()
    rdv_par_statut = serializers.DictField(child=serializers.IntegerField())


class ProRDVParIntervalleSerializer(serializers.Serializer):
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()
    total_rdv = serializers.IntegerField()
    rdv_par_statut = serializers.DictField(child=serializers.IntegerField())


class ProRDVAbsentSerializer(serializers.Serializer):
    nombre_clients_absents = serializers.IntegerField()

from rest_framework import serializers

class ProAbsentParServiceItemSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    service_nom = serializers.CharField()
    nombre_clients_absents = serializers.IntegerField()


class ProAbsentParServiceSerializer(serializers.Serializer):
    services = ProAbsentParServiceItemSerializer(many=True)

class ProRDVPresentSerializer(serializers.Serializer):
    nombre_clients_presents = serializers.IntegerField()



class ProPresentParServiceItemSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    service_nom = serializers.CharField()
    nombre_clients_presents = serializers.IntegerField()


class ProPresentParServiceSerializer(serializers.Serializer):
    services = ProPresentParServiceItemSerializer(many=True)


class FileDattenteStatsParMoisSerializer(serializers.Serializer):
    mois = serializers.IntegerField()
    annee = serializers.IntegerField()
    total_files = serializers.IntegerField()
    files_en_cours = serializers.IntegerField()
    files_terminees = serializers.IntegerField()
    files_suspendues = serializers.IntegerField()
    total_clients_dans_files = serializers.IntegerField()
    temps_moyen_attente_global = serializers.FloatField()


class ProFileAttenteStatsParAnneeSerializer(serializers.Serializer):
    annee = serializers.IntegerField()
    total_files = serializers.IntegerField()
    files_en_cours = serializers.IntegerField()
    files_terminees = serializers.IntegerField()
    files_suspendues = serializers.IntegerField()
    total_clients_dans_files = serializers.IntegerField()
    temps_moyen_attente_global = serializers.FloatField()


class ProFileAttenteStatsIntervalleSerializer(serializers.Serializer):
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()

    total_files = serializers.IntegerField()
    files_en_cours = serializers.IntegerField()
    files_terminees = serializers.IntegerField()
    files_suspendues = serializers.IntegerField()
    total_clients_dans_files = serializers.IntegerField()
    temps_moyen_attente_global = serializers.FloatField()



class ProTauxMoyenClientsParServiceSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    service_nom = serializers.CharField()
    nombre_files = serializers.IntegerField()
    total_clients = serializers.IntegerField()
    taux_moyen_clients = serializers.FloatField()