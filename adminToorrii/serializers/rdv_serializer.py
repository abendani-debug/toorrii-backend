from rest_framework import serializers
from adminToorrii.models import RDV, Client, Service, Ticket
from phonenumber_field.serializerfields import PhoneNumberField
from adminToorrii.utils.rdv_service import RDVCreationService

class RDVSerializer(serializers.ModelSerializer):
    # Champs supplémentaires en lecture seule pour faciliter le frontend
    client_nom = serializers.CharField(source='client.nom', read_only=True)
    client_prenom = serializers.CharField(source='client.prenom', read_only=True)
    service_nom = serializers.CharField(source='service.nom_service', read_only=True)

    class Meta:
        model = RDV
        fields = [
            "rdv_id",
            "client",
            "client_nom",
            "client_prenom",
            "service",
            "service_nom",
            "date_heure_rdv",
            "duree",
            "statut_rdv",
            "mode_reservation",
            "commentaire_client",
            "actif",
            "date_demande",
            "source_creation",
            "mail_envoye",
            "date_creation",
        ]
        read_only_fields = [
            "rdv_id",
            "date_creation",
            "client_nom",
            "client_prenom",
            "service_nom",
        ]


    
class CreateRDVSerializer(serializers.ModelSerializer):
    client_numero_telephone = PhoneNumberField(region='DZ', write_only=True, required=True)
    client_email = serializers.EmailField(required=False, allow_null=True, write_only=True)
    client_nom = serializers.CharField(max_length=50, required=False, allow_null=True, write_only=True)
    client_prenom = serializers.CharField(max_length=50, required=False, allow_null=True, write_only=True)

    service_id = serializers.CharField()

    class Meta:
        model = RDV
        fields = [
            "service_id",
            "date_heure_rdv",
            "client_numero_telephone",
            "client_email",
            "client_nom",
            "client_prenom",
            "commentaire_client",
            
        ]

    #  CREATE
    def create(self, validated_data):
        try:
            rdv, ticket = RDVCreationService.create_rdv(validated_data)
            return rdv
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

    #  UPDATE
    def update(self, instance, validated_data):
        try:
            rdv, ticket = RDVCreationService.update_rdv(instance, validated_data)
            return rdv
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

    #  REPRESENTATION (réponse API)
    def to_representation(self, instance):
        data = super().to_representation(instance)

        #  Infos client
        if instance.client:
            data["client"] = {
                "client_nom": instance.client.nom,
                "client_prenom": instance.client.prenom,
                "client_numero_telephone": str(instance.client.numero_telephone),
                "client_email": instance.client.email,
            }

        #  Infos service
        if instance.service:
            data["service"] = {
                "service_id": instance.service.service_id,
                "nom_service": getattr(instance.service, "nom_service", None)
            }

        #  Infos ticket
        ticket = Ticket.objects.filter(rdv=instance).first()
        if ticket:
            data["ticket"] = {
                "id": ticket.ticket_id,
                "position": ticket.position,
                "type_ticket": ticket.type_ticket,
                "creneau_prevue": ticket.creneau_prevue,
            }

        #  Nettoyage (optionnel)
        data.pop("service_id", None)

        return data



class AfficherListReservationSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    client_nom = serializers.SerializerMethodField()
    client_prenom = serializers.SerializerMethodField()
    client_numero_telephone = serializers.SerializerMethodField()
    client_email = serializers.SerializerMethodField()

    service = serializers.CharField(source='service.service_id', read_only=True)
    service_nom = serializers.CharField(source='service.nom_service', read_only=True)

    ticket_id = serializers.SerializerMethodField()
    ticket_position = serializers.SerializerMethodField()
    ticket_creneau = serializers.SerializerMethodField()
    ticket_type = serializers.SerializerMethodField()
    ticket_code = serializers.SerializerMethodField()

    class Meta:
        model = RDV
        fields = [
            "rdv_id",
            "client",#
            "client_nom",#
            "client_prenom",#
            "client_numero_telephone",#
            "client_email",#
            "service",#
            "service_nom",
            "date_heure_rdv",
            "statut_rdv",
            "duree",#
            "mode_reservation",
            "commentaire_client",
            "actif",
            "source_creation",
            "ticket_id",
            "ticket_position",
            "ticket_creneau",
            "ticket_type",
            "ticket_code"
        ]

    def get_client(self, obj):
        if obj.client:
            return f"{obj.client.id_client} "
        return None

    def get_client_nom(self, obj):
        if obj.client:
            return f"{obj.client.nom}"
        return None    

    def get_client_prenom(self, obj):
        if obj.client:
            return f"{obj.client.prenom}"
        return None

    def get_client_numero_telephone(self, obj):
        if obj.client:
            return f"{obj.client.numero_telephone}"
        return None

    def get_client_email(self, obj):
        if obj.client:
            return f"{obj.client.email}"
        return None

    def get_ticket(self, obj):
        return Ticket.objects.filter(rdv=obj).first()

    def get_ticket_id(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.ticket_id if ticket else None

    def get_ticket_position(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.position if ticket else None

    def get_ticket_creneau(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.creneau_prevue if ticket else None

    def get_ticket_type(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.type_ticket if ticket else None

    def get_ticket_code(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.code_ticket if ticket else None    



class AfficherReservationDetailRDVSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()
    client_nom = serializers.SerializerMethodField()
    client_prenom = serializers.SerializerMethodField()
    client_numero_telephone = serializers.SerializerMethodField()
    client_email = serializers.SerializerMethodField()

    service = serializers.CharField(source='service.service_id', read_only=True)
    service_nom = serializers.CharField(source='service.nom_service', read_only=True)
    service_prix = serializers.CharField(source='service.prix_service', read_only=True)
    nom_categorie = serializers.CharField(
    source="service.categorie.nom_categorie",
    read_only=True
)

    rdv_date_demande = serializers.CharField(source='rdv.date_creation', read_only=True)

    ticket_id = serializers.SerializerMethodField()
    ticket_position = serializers.SerializerMethodField()
    ticket_creneau = serializers.SerializerMethodField()
    ticket_type = serializers.SerializerMethodField()
    ticket_code = serializers.SerializerMethodField()
    ticket_notification = serializers.SerializerMethodField()
    ticket_date_validation = serializers.SerializerMethodField()
    ticket_date_creation = serializers.SerializerMethodField()

    class Meta:
        model = RDV
        fields = [
            "rdv_id",
            "client",
            "client_nom",
            "client_prenom",
            "client_numero_telephone",
            "client_email",
            "service",
            "service_nom",
            "service_prix",
            "nom_categorie",#
            "date_heure_rdv",
            "statut_rdv",
            "rdv_date_demande",
            "mail_envoye",
            "duree",
            "mode_reservation",
            "commentaire_client",
            "actif",
            "ticket_id",
            "ticket_position",
            "ticket_creneau",
            "ticket_type",
            "ticket_code",
            "ticket_notification",
            "ticket_date_validation",
            "ticket_date_creation"#
        ]

    def get_client(self, obj):
        if obj.client:
            return f"{obj.client.id_client} "
        return None

    def get_client_nom(self, obj):
        if obj.client:
            return f"{obj.client.nom}"
        return None    

    def get_client_prenom(self, obj):
        if obj.client:
            return f"{obj.client.prenom}"
        return None

    def get_client_numero_telephone(self, obj):
        if obj.client:
            return f"{obj.client.numero_telephone}"
        return None

    def get_client_email(self, obj):
        if obj.client:
            return f"{obj.client.email}"
        return None

    def get_ticket(self, obj):
        return Ticket.objects.filter(rdv=obj).first()

    def get_ticket_id(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.ticket_id if ticket else None

    def get_ticket_position(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.position if ticket else None

    def get_ticket_creneau(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.creneau_prevue if ticket else None

    def get_ticket_type(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.type_ticket if ticket else None

    def get_ticket_code(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.code_ticket if ticket else None

    def get_ticket_notification(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.notifie if ticket else None

    def get_ticket_date_validation(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.date_validation if ticket else None

    def get_ticket_date_creation(self, obj):
        ticket = self.get_ticket(obj)
        return ticket.date_creation if ticket else None


