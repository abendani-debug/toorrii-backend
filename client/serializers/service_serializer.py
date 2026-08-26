from rest_framework import serializers


class ServicePublicSerializer(serializers.Serializer):
    service_id = serializers.CharField()
    nom_service = serializers.CharField()
    description_service = serializers.CharField()
    prix_service = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    duree_moyenne_creneau = serializers.IntegerField()
    type_reservation = serializers.CharField()

    actif = serializers.BooleanField()
    date_creation = serializers.DateTimeField()

    photo_principal = serializers.ImageField(allow_null=True)


class ServicePlanningPauseSerializer(serializers.Serializer):
    description = serializers.CharField()
    heure_debut_pause = serializers.TimeField()
    heure_fin_pause = serializers.TimeField()


class ServicePlanningSerializer(serializers.Serializer):
    nom_jour = serializers.CharField()
    heure_debut_service = serializers.TimeField()
    heure_fin_service = serializers.TimeField()

    pauses = ServicePlanningPauseSerializer(many=True)


class ServiceExceptionSerializer(serializers.Serializer):
    raison = serializers.CharField()
    raison_autre = serializers.CharField(allow_null=True)
    date_debut_exception = serializers.DateField()
    date_fin_exception = serializers.DateField()
    heure_debut_exception = serializers.TimeField()
    heure_fin_exception = serializers.TimeField()


class ServiceDetailSerializer(serializers.Serializer):
    nom_service = serializers.CharField()
    description_service = serializers.CharField()
    prix_service = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    duree_moyenne_creneau = serializers.IntegerField()
    type_reservation = serializers.CharField()
    actif = serializers.BooleanField()
    date_creation = serializers.DateTimeField()
    photo_principal = serializers.ImageField(allow_null=True)

    planning = ServicePlanningSerializer(many=True)
    planning_exception = ServiceExceptionSerializer(many=True)