import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_client_rdv_notification(email: str, nom: str, date_rdv=None, service=None):
    """
    Envoie un email de confirmation RDV via Brevo
    """

    if not email:
        return None  # sécurité: pas d'email => rien envoyer

    # -----------------------------
    # CONFIG BREVO
    # -----------------------------
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # -----------------------------
    # CONTENU EMAIL
    # -----------------------------
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email, "name": nom}],
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": settings.DEFAULT_FROM_NAME
        },
        subject="Confirmation de votre rendez-vous",

        html_content=f"""
        <h2>Bonjour {nom},</h2>

        <p>Votre rendez-vous a été confirmé avec succès.</p>

        <hr>

        <p><strong>Détails du rendez-vous :</strong></p>

        <ul>
            <li>Date : {date_rdv if date_rdv else 'Non définie'}</li>
            <li>Service : {service if service else 'Non défini'}</li>
        </ul>

        <p>Merci de vous présenter à l'heure.</p>

        <br>

        <p>
            Cordialement,<br>
            <strong>L’équipe Toorrii</strong>
        </p>
        """
    )

    try:
        result = api_instance.send_transac_email(email_data)

        logger.info(
            "Email RDV envoyé à %s | Message ID: %s",
            email,
            result.message_id
        )

        return result

    except ApiException as e:
        logger.error(
            "Erreur Brevo email RDV %s | %s",
            email,
            str(e)
        )
        return None