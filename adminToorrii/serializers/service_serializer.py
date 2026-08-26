from rest_framework import serializers
from django.db import transaction
from adminToorrii.models import Categorie
from adminToorrii.models import (
    Service,
    ServicePlanning,
    ServicePlanningPause,
    ServicePlanningException
)

# ===============================
# PAUSE
# ===============================
class ServicePlanningPauseSerializer(serializers.ModelSerializer):
    service_planning_pause_id = serializers.CharField(required=False)

    class Meta:
        model = ServicePlanningPause
        fields = ["service_planning_pause_id", "description", "heure_debut_pause", "heure_fin_pause"]


# ===============================
# EXCEPTION
# ===============================
class ServicePlanningExceptionSerializer(serializers.ModelSerializer):
    service_planning_exception_id = serializers.CharField(required=False)

    class Meta:
        model = ServicePlanningException
        fields = [
            "service_planning_exception_id",
            "raison",
            "raison_autre",
            "date_debut_exception",
            "date_fin_exception",
            "heure_debut_exception",
            "heure_fin_exception",
        ]


# ===============================
# PLANNING
# ===============================
class ServicePlanningSerializer(serializers.ModelSerializer):
    service_planning_id = serializers.CharField(required=False)
    pauses = ServicePlanningPauseSerializer(many=True, required=False)

    class Meta:
        model = ServicePlanning
        fields = [
            "service_planning_id",
            "nom_jour",
            "heure_debut_service",
            "heure_fin_service",
            "pauses"
        ]


# ===============================
# MAIN SERIALIZER
# ===============================



class ServiceSerializer(serializers.ModelSerializer):
    planning = ServicePlanningSerializer(many=True, required=True)
    exceptions = ServicePlanningExceptionSerializer(many=True, required=False)

    class Meta:
        model = Service
        fields = [
            "service_id",
            "categorie",
            "nom_service",
            "description_service",
            "prix_service",
            "duree_moyenne_creneau",
            "actif",
            "date_creation",
            "photo_principal",
            "type_reservation",
            "planning",
            "exceptions",
        ]
        read_only_fields = ["service_id", "date_creation"]

    # ===============================
    # CREATE
    # ===============================
    @transaction.atomic
    def create(self, validated_data):
        planning_data = validated_data.pop("planning", [])
        exception_data = validated_data.pop("exceptions", [])

        service = Service.objects.create(**validated_data)

        for p in planning_data:
            pauses_data = p.pop("pauses", [])
            planning_obj = ServicePlanning.objects.create(service=service, **p)

            for pause in pauses_data:
                ServicePlanningPause.objects.create(
                    service_planning=planning_obj,
                    **pause
                )

        for e in exception_data:
            ServicePlanningException.objects.create(service=service, **e)

        return service

    # ===============================
    # UPDATE
    # ===============================
    @transaction.atomic
    def update(self, instance, validated_data):

        planning_data = validated_data.pop("planning", None)
        exception_data = validated_data.pop("exceptions", None)

        # =========================
        # UPDATE SERVICE FIELDS
        # =========================
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # =========================
        #  1. UPDATE PLANNING + PAUSES
        # =========================
        if planning_data is not None:

            existing_plannings = {
                p.service_planning_id: p
                for p in instance.planning.all()
            }

            for planning in planning_data:

                pauses_data = planning.pop("pauses", [])
                planning_id = planning.get("service_planning_id")

                #  SUPPRIMER si seulement l'id est envoyé
                if planning_id and len(planning) == 1:
                    if planning_id in existing_plannings:
                        existing_plannings[planning_id].delete()
                    continue

                # UPDATE
                if planning_id and planning_id in existing_plannings:
                    planning_instance = existing_plannings[planning_id]

                    for attr, value in planning.items():
                        if attr != "service_planning_id":
                            setattr(planning_instance, attr, value)

                    planning_instance.save()

                # CREATE
                else:
                    planning_instance = ServicePlanning.objects.create(
                        service=instance,
                        **{k: v for k, v in planning.items() if k != "service_planning_id"}
                    )

                # =========================
                #  PAUSES
                # =========================
                existing_pauses = {
                    p.service_planning_pause_id: p
                    for p in planning_instance.pauses.all()
                }

                for pause in pauses_data:

                    pause_id = pause.get("service_planning_pause_id")

                    #  SUPPRIMER si seulement l'id est envoyé
                    if pause_id and len(pause) == 1:
                        if pause_id in existing_pauses:
                            existing_pauses[pause_id].delete()
                        continue

                    # UPDATE
                    if pause_id and pause_id in existing_pauses:
                        pause_instance = existing_pauses[pause_id]

                        for attr, value in pause.items():
                            if attr != "service_planning_pause_id":
                                setattr(pause_instance, attr, value)

                        pause_instance.save()

                    # CREATE
                    else:
                        ServicePlanningPause.objects.create(
                            service_planning=planning_instance,
                            **{k: v for k, v in pause.items() if k != "service_planning_pause_id"}
                        )

        # =========================
        #  2. UPDATE EXCEPTIONS
        # =========================
        if exception_data is not None:

            existing_exceptions = {
                e.service_planning_exception_id: e
                for e in instance.planning_exception.all()
            }

            for exc in exception_data:

                exc_id = exc.get("service_planning_exception_id")

                #  SUPPRIMER si seulement l'id est envoyé
                if exc_id and len(exc) == 1:
                    if exc_id in existing_exceptions:
                        existing_exceptions[exc_id].delete()
                    continue

                # UPDATE
                if exc_id and exc_id in existing_exceptions:
                    exc_instance = existing_exceptions[exc_id]

                    for attr, value in exc.items():
                        if attr != "service_planning_exception_id":
                            setattr(exc_instance, attr, value)

                    exc_instance.save()

                # CREATE
                else:
                    ServicePlanningException.objects.create(
                        service=instance,
                        **{k: v for k, v in exc.items() if k != "service_planning_exception_id"}
                    )

        return instance   
    




# -------------------------------
# PAUSE (lecture)
# -------------------------------
class ServicePlanningPauseReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePlanningPause
        fields = [
            "service_planning_pause_id",
            "description",
            "heure_debut_pause",
            "heure_fin_pause"
        ]


# -------------------------------
# PLANNING (lecture)
# -------------------------------
class ServicePlanningReadSerializer(serializers.ModelSerializer):
    pauses = ServicePlanningPauseReadSerializer(many=True)

    class Meta:
        model = ServicePlanning
        fields = [
            "service_planning_id",
            "nom_jour",
            "heure_debut_service",
            "heure_fin_service",
            "pauses"
        ]


# -------------------------------
# EXCEPTION (lecture)
# -------------------------------
class ServicePlanningExceptionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePlanningException
        fields = [
            "service_planning_exception_id",
            "raison",
            "raison_autre",
            "date_debut_exception",
            "date_fin_exception",
            "heure_debut_exception",
            "heure_fin_exception"
        ]

class CategorieReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ["categorie_id","nom_categorie"]
# -------------------------------
# SERVICE DETAIL
# -------------------------------
class ServiceDetailSerializer(serializers.ModelSerializer):
    planning = ServicePlanningReadSerializer( many=True, read_only=True)
    exceptions = ServicePlanningExceptionReadSerializer(
        source="planning_exception",
        many=True,
        read_only=True
    )
    categorie = CategorieReadSerializer(read_only=True)

    class Meta:
        model = Service
        fields = [
            "service_id",
            "categorie",
            "nom_service",
            "description_service",
            "prix_service",
            "duree_moyenne_creneau",
            "actif",
            "photo_principal",
            "type_reservation",
            "date_creation",
            "planning",
            "exceptions"
        ]
     