# services/rdv_service.py
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from adminToorrii.models import (
    Service,
    Client,
    RDV,
    Ticket,
    ServicePlanning,
    ServicePlanningPause,
    ServicePlanningException,
    FileDattente
)


class RDVCreationService:

    @staticmethod
    def get_day_name(dt):
        jours = {
            0: "LUNDI",
            1: "MARDI",
            2: "MERCREDI",
            3: "JEUDI",
            4: "VENDREDI",
            5: "SAMEDI",
            6: "DIMANCHE",
        }
        return jours[dt.weekday()]

    @staticmethod
    def check_exception(service, date_reservation, heure):
        exceptions = ServicePlanningException.objects.filter(
            service=service,
            date_debut_exception__lte=date_reservation,
            date_fin_exception__gte=date_reservation,
        )

        for exc in exceptions:
            if exc.heure_debut_exception <= heure <= exc.heure_fin_exception:
                raise Exception("Service indisponible (exception planning)")

    @staticmethod
    def check_pause(planning, heure):
        pauses = ServicePlanningPause.objects.filter(service_planning=planning)

        for pause in pauses:
            if pause.heure_debut_pause <= heure < pause.heure_fin_pause:
                raise Exception("Créneau dans une pause du service")

    @staticmethod
    def check_creneau_disponible(service, date_heure):

    # Vérifier que la date n'est pas passée
        if date_heure < timezone.now():
            raise Exception(
                "Impossible de réserver un créneau dans le passé"
            )

        duree = service.duree_moyenne_creneau

        debut_nouveau = date_heure
        fin_nouveau = date_heure + timedelta(minutes=duree)

        rdvs = RDV.objects.filter(service=service)

        for rdv in rdvs:

            debut_existant = rdv.date_heure_rdv
            fin_existant = rdv.date_heure_rdv + timedelta(
                minutes=service.duree_moyenne_creneau
            )

            chevauchement = (
                debut_nouveau < fin_existant
                and fin_nouveau > debut_existant
            )

            if chevauchement:
                raise Exception(
                    "Ce créneau chevauche un autre rendez-vous"
                )

    @staticmethod
    @transaction.atomic
    def create_rdv(data):
        client, created = Client.objects.get_or_create(
                numero_telephone=data["client_numero_telephone"],
                defaults={
                    "nom": data.get("client_nom"),
                    "prenom": data.get("client_prenom"),
                    "email": data.get("client_email"),
                }
        )

        service = Service.objects.filter(service_id=data["service_id"], actif=True).first()
        if not service:
            raise Exception("Service introuvable ou inactif")

        date_heure = data["date_heure_rdv"]
        date_res = date_heure.date()
        heure_res = date_heure.time()

        # Vérifier exception planning
        RDVCreationService.check_exception(service, date_res, heure_res)

        # Vérifier jour de travail
        nom_jour = RDVCreationService.get_day_name(date_heure)

        planning = ServicePlanning.objects.filter(
            service=service,
            nom_jour=nom_jour
        ).first()

        if not planning:
            raise Exception("Service non disponible ce jour")

        # Vérifier horaires service
        if not (planning.heure_debut_service <= heure_res <= planning.heure_fin_service):
            raise Exception("Créneau hors horaires du service")

        # Vérifier pause
        RDVCreationService.check_pause(planning, heure_res)

        # Vérifier disponibilité créneau
        RDVCreationService.check_creneau_disponible(service, date_heure)

        

        # Récupérer ou créer file d’attente du jour
        file_dattente, _ = FileDattente.objects.get_or_create(
            service=service,
            date_jour=date_heure.date(),
            professionnel=service.professionnel,
            temps_moyen_attente=service.duree_moyenne_creneau
        )

        # Création RDV
        rdv = RDV.objects.create(
            client=client,
            service=service,
            file_dattente=file_dattente,
            date_heure_rdv=date_heure,
            duree=service.duree_moyenne_creneau,
            statut_rdv="Confirmer",
            mode_reservation="En_ligne",
            commentaire_client=data.get("commentaire_client", ""),
            actif=True,
            source_creation="Pro"
        )

        # Calcul position ticket
        last_position = Ticket.objects.filter(
            file_attente=file_dattente
        ).count()

        position = last_position + 1

        # Création Ticket OBLIGATOIRE
        ticket = Ticket.objects.create(
            client=client,
            file_attente=file_dattente,
            rdv=rdv,
            type_ticket="RDV",
            position=position,
            creneau_prevue=date_heure,
        )
        #  Mise à jour du nombre de clients dans la file d'attente
        file_dattente.nombre_clients = (file_dattente.nombre_clients or 0) + 1
        file_dattente.save(update_fields=["nombre_clients"])


        return rdv, ticket

    @staticmethod
    @transaction.atomic
    def update_rdv(rdv, data):
    
        service = rdv.service
        client = rdv.client
    
        old_file = rdv.file_dattente  #  sauvegarde ancienne file
    
        # =========================
        # NOUVELLES VALEURS
        # =========================
        date_heure = data.get("date_heure_rdv", rdv.date_heure_rdv)
        mode_reservation = data.get("mode_reservation", rdv.mode_reservation)
        commentaire = data.get("commentaire_client", rdv.commentaire_client)
    
        date_res = date_heure.date()
        heure_res = date_heure.time()
    
        # =========================
        # VALIDATIONS MÉTIER
        # =========================
        RDVCreationService.check_exception(service, date_res, heure_res)
    
        nom_jour = RDVCreationService.get_day_name(date_heure)
    
        planning = ServicePlanning.objects.filter(
            service=service,
            nom_jour=nom_jour
        ).first()
    
        if not planning:
            raise Exception("Service non disponible ce jour")
    
        if not (planning.heure_debut_service <= heure_res <= planning.heure_fin_service):
            raise Exception("Créneau hors horaires du service")
    
        RDVCreationService.check_pause(planning, heure_res)
    
        exists = RDV.objects.filter(
            service=service,
            date_heure_rdv=date_heure
        ).exclude(rdv_id=rdv.rdv_id).exists()
    
        if exists:
            raise Exception("Ce créneau est déjà réservé")
    
        # =========================
        # FILE D'ATTENTE (NEW)
        # =========================
        new_file, _ = FileDattente.objects.get_or_create(
            service=service,
            date_jour=date_res,
            professionnel=service.professionnel,
            temps_moyen_attente=service.duree_moyenne_creneau
        )
    
        # =========================
        # UPDATE RDV
        # =========================
        rdv.date_heure_rdv = date_heure
        rdv.mode_reservation = mode_reservation
        rdv.commentaire_client = commentaire
        rdv.file_dattente = new_file
        rdv.save()

        # =========================
        # UPDATE TICKET
        # =========================
        ticket = Ticket.objects.filter(rdv=rdv).first()

        if not ticket:
            raise Exception("Ticket associé introuvable")

        #  si changement de file
        if ticket.file_attente != new_file:

            #  décrémenter ancienne file
            if old_file:
                FileDattente.objects.filter(pk=old_file.pk).update(
                    nombre_clients=F("nombre_clients") - 1
                )

            #  incrémenter nouvelle file
            FileDattente.objects.filter(pk=new_file.pk).update(
                nombre_clients=F("nombre_clients") + 1
            )

            ticket.file_attente = new_file

            # recalcul position
            last_position = Ticket.objects.filter(
                file_attente=new_file
            ).count()

            ticket.position = last_position + 1

        # =========================
        # UPDATE TICKET DATA
        # =========================
        ticket.creneau_prevue = date_heure
        ticket.save()

        return rdv, ticket