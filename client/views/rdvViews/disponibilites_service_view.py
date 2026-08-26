from datetime import datetime, timedelta, date as date_type, time as time_type
from django.utils.timezone import make_aware
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample,
)

from adminToorrii.models import Service, RDV


# ── Mapping nom_jour → numéro de jour Python (Monday=0 … Sunday=6) ──────────
JOUR_TO_WEEKDAY = {
    "LUNDI":    0,
    "MARDI":    1,
    "MERCREDI": 2,
    "JEUDI":    3,
    "VENDREDI": 4,
    "SAMEDI":   5,
    "DIMANCHE": 6,
}

STATUTS_ACTIFS = ["En_attente", "Confirmer"]


def _time_to_minutes(t: time_type) -> int:
    return t.hour * 60 + t.minute


def _minutes_to_str(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _str_to_minutes(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


class DisponibilitesServiceView(APIView):
    """
    Retourne les créneaux disponibles d'un service pour une date donnée.
    Chaque créneau indique s'il est disponible ou déjà réservé.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Services Client"],
        summary="Créneaux disponibles d'un service",
        description=(
            "Retourne la liste des créneaux horaires générés par le planning du service "
            "pour la date demandée, en indiquant pour chacun s'il est disponible ou pris.\n\n"
            "Un créneau est **pris** s'il existe un RDV avec statut `En_attente` ou `Confirmer` "
            "sur ce service à cette heure exacte.\n\n"
            "Un créneau est **absent** si le jour est fermé (aucun planning) ou si la date "
            "tombe dans une exception planning."
        ),
        parameters=[
            OpenApiParameter(
                name="service_id",
                type=str,
                location=OpenApiParameter.PATH,
                required=True,
                description="Identifiant du service (ex: SER_1)"
            ),
            OpenApiParameter(
                name="date",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Date au format YYYY-MM-DD (ex: 2026-07-30)"
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Liste des créneaux avec leur disponibilité",
                examples=[
                    OpenApiExample(
                        name="Exemple réponse",
                        value={
                            "service_id": "SER_1",
                            "date": "2026-07-30",
                            "duree_creneau": 30,
                            "ouvert": True,
                            "exception": False,
                            "creneaux": [
                                {"heure": "09:00", "disponible": True},
                                {"heure": "09:30", "disponible": False},
                                {"heure": "10:00", "disponible": True},
                            ]
                        },
                        response_only=True,
                        status_codes=["200"]
                    )
                ]
            ),
            400: OpenApiResponse(description="Paramètre date manquant ou invalide"),
            404: OpenApiResponse(description="Service introuvable"),
        }
    )
    def get(self, request, service_id):

        # ── 1. Récupérer le service ──────────────────────────────────────────
        try:
            service = Service.objects.prefetch_related(
                "planning__pauses",
                "planning_exception"
            ).get(pk=service_id)
        except Service.DoesNotExist:
            return Response(
                {"error": "Service introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ── 2. Valider le paramètre date ─────────────────────────────────────
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"error": "Le paramètre 'date' est obligatoire (format: YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_date: date_type = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Format de date invalide. Utiliser YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        duree = service.duree_moyenne_creneau

        # ── 3. Vérifier si le jour est une exception planning ────────────────
        is_exception = service.planning_exception.filter(
            date_debut_exception__lte=target_date,
            date_fin_exception__gte=target_date,
        ).exists()

        if is_exception:
            return Response({
                "service_id": service_id,
                "date": date_str,
                "duree_creneau": duree,
                "ouvert": False,
                "exception": True,
                "creneaux": [],
            })

        # ── 4. Trouver le planning du jour ───────────────────────────────────
        # Python weekday() : 0=Lundi … 6=Dimanche
        weekday = target_date.weekday()
        plan_jour = None
        for p in service.planning.all():
            if JOUR_TO_WEEKDAY.get(p.nom_jour) == weekday:
                plan_jour = p
                break

        if plan_jour is None:
            return Response({
                "service_id": service_id,
                "date": date_str,
                "duree_creneau": duree,
                "ouvert": False,
                "exception": False,
                "creneaux": [],
            })

        # ── 5. Générer les créneaux depuis le planning ───────────────────────
        debut_min = _time_to_minutes(plan_jour.heure_debut_service)
        fin_min   = _time_to_minutes(plan_jour.heure_fin_service)

        pauses = [
            {
                "debut": _time_to_minutes(pause.heure_debut_pause),
                "fin":   _time_to_minutes(pause.heure_fin_pause),
            }
            for pause in plan_jour.pauses.all()
        ]

        creneaux_heures = []
        cursor = debut_min
        while cursor + duree <= fin_min:
            slot_end = cursor + duree
            in_pause = any(
                cursor < p["fin"] and slot_end > p["debut"]
                for p in pauses
            )
            if not in_pause:
                creneaux_heures.append(_minutes_to_str(cursor))
            cursor += duree

        # ── 5b. Filtrer les créneaux passés si la date est aujourd'hui ──────
        if target_date == date_type.today():
            from django.utils import timezone as tz
            now_local = tz.localtime(tz.now())
            now_minutes = now_local.hour * 60 + now_local.minute
            creneaux_heures = [h for h in creneaux_heures if _str_to_minutes(h) > now_minutes]

        # ── 6. Récupérer les RDV actifs sur ce service pour cette date ───────
        debut_journee = make_aware(datetime.combine(target_date, time_type.min))
        fin_journee   = make_aware(datetime.combine(target_date, time_type.max))

        rdvs_actifs = RDV.objects.filter(
            service=service,
            statut_rdv__in=STATUTS_ACTIFS,
            date_heure_rdv__gte=debut_journee,
            date_heure_rdv__lte=fin_journee,
        ).values_list("date_heure_rdv", flat=True)

        # Convertir en ensemble d'heures "HH:MM" pour comparaison rapide
        heures_prises = set()
        for rdv_dt in rdvs_actifs:
            heures_prises.add(f"{rdv_dt.hour:02d}:{rdv_dt.minute:02d}")

        # ── 7. Construire la réponse ─────────────────────────────────────────
        creneaux = [
            {
                "heure": heure,
                "disponible": heure not in heures_prises,
            }
            for heure in creneaux_heures
        ]

        return Response({
            "service_id": service_id,
            "date": date_str,
            "duree_creneau": duree,
            "ouvert": True,
            "exception": False,
            "creneaux": creneaux,
        })
