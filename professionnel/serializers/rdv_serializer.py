from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

from adminToorrii.models import RDV, Ticket
from professionnel.utils.rdv_service import RDVCreationService


class RdvSerializer(serializers.ModelSerializer):
    client_numero_telephone = PhoneNumberField(region='DZ', write_only=True, required=True)
    client_email = serializers.EmailField(required=False, allow_null=True, write_only=True)
    client_nom = serializers.CharField(max_length=50, required=False, allow_null=True, write_only=True)
    client_prenom = serializers.CharField(max_length=50, required=False, allow_null=True, write_only=True)
    commentaire_client = serializers.CharField(max_length=50, required=False, allow_null=True)

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
                "nom": instance.client.nom,
                "prenom": instance.client.prenom,
                "numero_telephone": str(instance.client.numero_telephone),
                "email": instance.client.email
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
                "ticket_id": ticket.ticket_id,
                "position": ticket.position,
                "type_ticket": ticket.type_ticket,
                "creneau_prevue": ticket.creneau_prevue
            }

        #  Nettoyage 
        data.pop("service_id", None)

        return data



class RdvDetailSerializer(serializers.ModelSerializer):

    client = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    ticket = serializers.SerializerMethodField()

    class Meta:
        model = RDV
        fields = [
            "rdv_id",
            "date_heure_rdv",
            "duree",
            "statut_rdv",
            "mode_reservation",
            "commentaire_client",
            "date_creation",
            "client",
            "service",
            "ticket"
        ]

    def get_client(self, obj):
        if not obj.client:
            return None

        return {
            "nom": obj.client.nom,
            "prenom": obj.client.prenom,
            "numero_telephone": str(obj.client.numero_telephone),
            "email": obj.client.email
        }

    def get_service(self, obj):
        return {
            "id": obj.service.service_id,
            "nom": obj.service.nom_service
        }

    def get_ticket(self, obj):
        ticket = Ticket.objects.filter(rdv=obj).first()

        if not ticket:
            return None

        return {
            "id": ticket.ticket_id,
            "position": ticket.position,
            "type_ticket": ticket.type_ticket,
            "creneau_prevue": ticket.creneau_prevue
        }


class RdvListSerializer(serializers.ModelSerializer):

    client = serializers.SerializerMethodField()
    service = serializers.SerializerMethodField()
    ticket = serializers.SerializerMethodField()

    class Meta:
        model = RDV
        fields = [
            "rdv_id",
            "date_heure_rdv",
            "duree",
            "statut_rdv",
            "mode_reservation",
            "client",
            "service",
            "ticket"
        ]

    def get_client(self, obj):
        if not obj.client:
            return None

        return {
            "nom": obj.client.nom,
            "prenom": obj.client.prenom,
            "telephone": str(obj.client.numero_telephone),
        }

    def get_service(self, obj):
        return {
            "service_id": obj.service.service_id,
            "nom": obj.service.nom_service
        }

    def get_ticket(self, obj):
        ticket = Ticket.objects.filter(rdv=obj).first()

        if not ticket:
            return None

        return {
            "ticket_id": ticket.ticket_id,
            "position": ticket.position,
            "type": ticket.type_ticket
        }