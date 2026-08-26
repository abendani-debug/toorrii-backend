import json
from django.db import transaction
from rest_framework import serializers
from datetime import time, datetime

from adminToorrii.models import (
    Service,
    ServicePlanning,
    ServicePlanningPause,
    ServicePlanningException,
    Categorie
)

# ===============================
# PAUSE
# ===============================
class ServicePlanningPauseSerializer(serializers.ModelSerializer):
    pause_id = serializers.CharField(
        source="service_planning_pause_id",
        required=False
    )

    class Meta:
        model = ServicePlanningPause
        fields = [
            "pause_id",
            "description",
            "heure_debut_pause",
            "heure_fin_pause"
        ]


# ===============================
# EXCEPTION
# ===============================
class ServicePlanningExceptionSerializer(serializers.ModelSerializer):
    exception_id = serializers.CharField(
        source="service_planning_exception_id",
        required=False
    )

    class Meta:
        model = ServicePlanningException
        fields = [
            "exception_id",
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
    pauses = ServicePlanningPauseSerializer(many=True, required=False)

    class Meta:
        model = ServicePlanning
        fields = [
            "nom_jour",
            "heure_debut_service",
            "heure_fin_service",
            "pauses"
        ]


# ===============================
# SERVICE SERIALIZER (FIX COMPLET)
# ===============================
from datetime import time
from django.db import transaction
from rest_framework import serializers

from adminToorrii.models import (
    Service,
    ServicePlanning,
    ServicePlanningPause,
    ServicePlanningException,
)


# ===============================
# UTILS (SENIOR)
# ===============================
def time_to_minutes(t):
    if isinstance(t, str):
        t = datetime.strptime(t, "%H:%M").time()
    return t.hour * 60 + t.minute


def calculate_work_minutes(day):
    start = time_to_minutes(day["heure_debut_service"])
    end = time_to_minutes(day["heure_fin_service"])

    if end <= start:
        raise serializers.ValidationError(
            f"Heures invalides pour le jour {day.get('nom_jour')}"
        )

    total = end - start

    pauses = day.get("pauses", [])
    pause_total = 0

    for p in pauses:
        p_start = time_to_minutes(p["heure_debut_pause"])
        p_end = time_to_minutes(p["heure_fin_pause"])

        if p_end <= p_start:
            raise serializers.ValidationError(
                f"Pause invalide dans le jour {day.get('nom_jour')}"
            )

        pause_total += (p_end - p_start)

    work_time = total - pause_total

    if work_time <= 0:
        raise serializers.ValidationError(
            f"Temps de travail invalide pour {day.get('nom_jour')}"
        )

    return work_time


# ===============================
# SERIALIZER
# ===============================
class ServiceSerializer(serializers.ModelSerializer):
    planning = serializers.ListField()
    exceptions = serializers.ListField(required=False)

    class Meta:
        model = Service
        fields = [
            "service_id",
            "categorie",
            "nom_service",
            "description_service",
            "prix_service",
            "duree_moyenne_creneau",
            "photo_principal",
            "type_reservation",
            "planning",
            "exceptions",
        ]
        read_only_fields = ["service_id"]

    # ===============================
    # VALIDATION PRINCIPALE (SENIOR)
    # ===============================
    def validate(self, attrs):
        request = self.context.get("request")

        if not request or not hasattr(request.user, "professionnel_profile"):
            raise serializers.ValidationError(
                "Utilisateur non professionnel ou non authentifié."
            )

        duree = attrs.get("duree_moyenne_creneau")
        planning = attrs.get("planning")

        #  CAS UPDATE → récupérer planning depuis DB si absent
        if not planning and self.instance:
            planning_qs = ServicePlanning.objects.filter(service=self.instance)

            planning = []
            for p in planning_qs:
                pauses = ServicePlanningPause.objects.filter(service_planning=p)

                planning.append({
                    "nom_jour": p.nom_jour,
                    "heure_debut_service": p.heure_debut_service,
                    "heure_fin_service": p.heure_fin_service,
                    "pauses": [
                        {
                            "heure_debut_pause": pause.heure_debut_pause,
                            "heure_fin_pause": pause.heure_fin_pause,
                        }
                        for pause in pauses
                    ]
                })

        if not planning:
            raise serializers.ValidationError(
                "Le planning est obligatoire pour valider la durée."
            )

        #  Calcul du jour minimum
        min_work_time = None

        for day in planning:
            work_time = calculate_work_minutes(day)

            if min_work_time is None or work_time < min_work_time:
                min_work_time = work_time

        if duree > min_work_time:
            raise serializers.ValidationError({
                "duree_moyenne_creneau":
                    f"La durée ({duree} min) dépasse le temps minimum disponible ({min_work_time} min)."
            })

        return attrs

    # ===============================
    # CREATE
    # ===============================
    @transaction.atomic
    def create(self, validated_data):
        planning_data = validated_data.pop("planning", [])
        exceptions_data = validated_data.pop("exceptions", [])

        service = Service.objects.create(**validated_data)

        # Planning
        for p in planning_data:
            pauses_data = p.pop("pauses", [])

            planning_obj = ServicePlanning.objects.create(
                service=service,
                **p
            )

            for pause in pauses_data:
                ServicePlanningPause.objects.create(
                    service_planning=planning_obj,
                    **pause
                )

        # Exceptions
        for e in exceptions_data:
            ServicePlanningException.objects.create(
                service=service,
                **e
            )

        return service

    # ===============================
    # UPDATE (SENIOR)
    # ===============================
    @transaction.atomic
    def update(self, instance, validated_data):
        planning_data = validated_data.pop("planning", [])
        exceptions_data = validated_data.pop("exceptions", [])

        # Update champs service
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # -------------------------
        # PLANNING
        # -------------------------
        for planning_item in planning_data:
            pauses_data = planning_item.pop("pauses", [])

            planning_obj, _ = ServicePlanning.objects.update_or_create(
                service=instance,
                nom_jour=planning_item["nom_jour"],
                defaults={
                    "heure_debut_service": planning_item["heure_debut_service"],
                    "heure_fin_service": planning_item["heure_fin_service"],
                }
            )

            # PAUSES
            for pause in pauses_data:
                pause_id = pause.get("service_planning_pause_id")

                # DELETE
                if pause_id and len(pause) == 1:
                    ServicePlanningPause.objects.filter(
                        service_planning=planning_obj,
                        service_planning_pause_id=pause_id
                    ).delete()
                    continue

                # UPDATE
                if pause_id:
                    ServicePlanningPause.objects.filter(
                        service_planning_pause_id=pause_id
                    ).update(
                        description=pause.get("description"),
                        heure_debut_pause=pause.get("heure_debut_pause"),
                        heure_fin_pause=pause.get("heure_fin_pause"),
                    )
                else:
                    # CREATE
                    ServicePlanningPause.objects.create(
                        service_planning=planning_obj,
                        **pause
                    )

        # -------------------------
        # EXCEPTIONS
        # -------------------------
        for exception in exceptions_data:
            exception_id = exception.get("service_planning_exception_id")

            # DELETE
            if exception_id and len(exception) == 1:
                ServicePlanningException.objects.filter(
                    service=instance,
                    service_planning_exception_id=exception_id
                ).delete()
                continue

            # UPDATE
            if exception_id:
                ServicePlanningException.objects.filter(
                    service_planning_exception_id=exception_id
                ).update(**exception)
            else:
                # CREATE
                ServicePlanningException.objects.create(
                    service=instance,
                    **exception
                )

        return instance


# ===============================
# PAUSES
# ===============================
class ServicePlanningPauseReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePlanningPause
        fields = [
            "service_planning_pause_id",
            "description",
            "heure_debut_pause",
            "heure_fin_pause"
        ]


# ===============================
# PLANNING
# ===============================
class ServicePlanningReadSerializer(serializers.ModelSerializer):
    pauses = ServicePlanningPauseReadSerializer(many=True, read_only=True)

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
# EXCEPTIONS
# ===============================
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
# ===============================
# SERVICE DETAIL (IMPORTANT)
# ===============================
class ServiceDetailSerializer(serializers.ModelSerializer):

    planning = ServicePlanningReadSerializer(many=True, read_only=True)
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