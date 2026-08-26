from rest_framework import serializers
from adminToorrii.models import FileDattente, Ticket
from phonenumber_field.serializerfields import PhoneNumberField

class FileDattenteSerializer(serializers.ModelSerializer):
    service_nom = serializers.CharField(source="service.nom_service", read_only=True)
    professionnel_nom = serializers.CharField(source="professionnel.nom_entreprise", read_only=True)
    service_id = serializers.CharField(source="service.service_id", read_only=True)

    class Meta:
        model = FileDattente
        fields = [
            "file_id",
            "service_id",
            "service_nom",
            "professionnel_nom",
            "date_jour",
            "temps_moyen_attente",
            "etat_file",
            "nombre_clients",
            "date_creation"
        ]

class TicketFileSerializer(serializers.ModelSerializer):
    nom_client = serializers.CharField(source="client.nom", read_only=True, allow_null=True)
    prenom_client = serializers.CharField(source="client.prenom", read_only=True, allow_null=True)
    numero_telephone = serializers.CharField(source="client.numero_telephone", read_only=True, allow_null=True)
    email = serializers.EmailField(source="client.email", read_only=True, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            "ticket_id",
            "position",
            "type_ticket",
            "creneau_prevue",
            "code_ticket",
            "date_creation",
            "etat_ticket",
            "est_actif_dans_file",
            "nom_client",
            "prenom_client",
            "numero_telephone",
            "email",
        ]

class FileDattenteDetailSerializer(serializers.ModelSerializer):

    service_nom = serializers.CharField(source="service.nom_service", read_only=True)
    service_id = serializers.CharField(source="service.service_id", read_only=True)

    professionnel_nom = serializers.CharField(
        source="professionnel.nom_entreprise",
        read_only=True
    )

    tickets = serializers.SerializerMethodField()

    class Meta:
        model = FileDattente
        fields = [
            "file_id",
            "service_id",
            "service_nom",
            "professionnel_nom",
            "date_jour",
            "temps_moyen_attente",
            "etat_file",
            "nombre_clients",
            "date_creation",
            "tickets"
        ]

    def get_tickets(self, obj):
        tickets = Ticket.objects.filter(
            file_attente=obj,
            est_actif_dans_file=True
        ).order_by("position")
        return TicketFileSerializer(tickets, many=True).data


class AjouterClientFileAttenteSerializer(serializers.Serializer):

    client_numero_telephone = PhoneNumberField(region='DZ', required=True)
    client_nom = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    client_prenom = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    client_email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)

    def validate(self, attrs):
        """
        Validation métier simple
        """
        if not attrs.get("client_numero_telephone"):
            raise serializers.ValidationError({
                "client_numero_telephone": "Ce champ est obligatoire"
            })

        return attrs

class ModifierPositionClientSerializer(serializers.Serializer):
    nouvelle_position = serializers.IntegerField(min_value=1)