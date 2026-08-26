from rest_framework import serializers
from adminToorrii.models import FileDattente, Ticket
from phonenumber_field.serializerfields import PhoneNumberField

class FileDattenteSerializer(serializers.ModelSerializer):

    service_nom = serializers.CharField(source="service.nom_service", read_only=True)
    service_id = serializers.CharField(source="service.service_id", read_only=True)

    professionnel_id = serializers.CharField(source="professionnel.professionnel_id", read_only=True)
    professionnel_nom = serializers.CharField(source="professionnel.nom_entreprise", read_only=True)
    date_creation_FA = serializers.DateTimeField(
        source="date_creation",
        read_only=True,
        format="%Y-%m-%dT%H:%M:%S.%f%z"
    )

    class Meta:
        model = FileDattente
        fields = [
            "file_id",
            "service_id",
            "service_nom",
            "professionnel_id",
            "professionnel_nom",
            "date_jour",
            "temps_moyen_attente",
            "etat_file",
            "nombre_clients",
            "date_creation_FA",
        ]



class TicketFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            "ticket_id",
            "position",
            "type_ticket",
            "creneau_prevue",
            "code_ticket",
            "date_creation"
        ]


class FileDattenteDetailSerializer(serializers.ModelSerializer):

    service_nom = serializers.CharField(source="service.nom_service", read_only=True)
    service_id = serializers.CharField(source="service.service_id", read_only=True)

    professionnel_id = serializers.CharField(source="professionnel.professionnel_id", read_only=True)
    professionnel_nom = serializers.CharField(source="professionnel.nom_entreprise", read_only=True)

    #  catégorie via service
    categorie_nom = serializers.CharField(
        source="service.categorie.nom_categorie",
        read_only=True
    )

    date_creation_FA = serializers.DateTimeField(
        source="date_creation",
        read_only=True,
        format="%Y-%m-%dT%H:%M:%S.%f%z"
    )

    #  tickets (relation custom)
    tickets = serializers.SerializerMethodField()

    class Meta:
        model = FileDattente
        fields = [
            "file_id",
            "categorie_nom",
            "service_id",
            "service_nom",
            "professionnel_id",
            "professionnel_nom",
            "date_jour",
            "temps_moyen_attente",
            "etat_file",
            "nombre_clients",
            "date_creation_FA",
            "tickets"
        ]

    #  récupérer tous les tickets de la file
    def get_tickets(self, obj):
        tickets = Ticket.objects.filter(file_attente=obj).order_by("position")
        return TicketFileSerializer(tickets, many=True).data