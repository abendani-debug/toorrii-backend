import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_rdv_validation_notification(email: str, nom: str, date_rdv=None, service=None):
    """
    Notification envoyée quand un professionnel valide un RDV
    """

    if not email:
        return None

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email, "name": nom}],
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": settings.DEFAULT_FROM_NAME
        },
        subject="Votre rendez-vous a été confirmé ✔",

        html_content=f"""
        <h2>Bonjour {nom},</h2>

        <p>Bonne nouvelle </p>

        <p>Votre rendez-vous a été <strong>confirmé</strong> par le professionnel.</p>

        <hr>

        <p><strong>Détails :</strong></p>
        <ul>
            <li>Date : {date_rdv}</li>
            <li>Service : {service}</li>
        </ul>

        <p>Merci de vous présenter à l'heure.</p>

        <br>

        <p>L’équipe Toorrii</p>
        """
    )

    try:
        result = api_instance.send_transac_email(email_data)

        logger.info(
            "RDV validation email envoyé à %s | %s",
            email,
            result.message_id
        )

        return result

    except ApiException as e:
        logger.error("Erreur email validation RDV %s", str(e))
        return None
    

def send_rdv_cancellation_notification(email: str, nom: str, date_rdv=None, service=None):
    """
    Notification envoyée quand un professionnel annule un RDV
    """

    if not email:
        return None

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email, "name": nom}],
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": settings.DEFAULT_FROM_NAME
        },
        subject="Votre rendez-vous a été annulé ❌",

        html_content=f"""
        <h2>Bonjour {nom},</h2>

        <p>Nous vous informons que votre rendez-vous a été <strong>annulé</strong> par le professionnel.</p>

        <hr>

        <p><strong>Détails :</strong></p>
        <ul>
            <li>Date : {date_rdv}</li>
            <li>Service : {service}</li>
        </ul>

        <p>Veuillez reprendre un autre rendez-vous si nécessaire.</p>

        <br>

        <p>L’équipe Toorrii</p>
        """
    )

    try:
        result = api_instance.send_transac_email(email_data)

        logger.info(
            "Email annulation RDV envoyé à %s | %s",
            email,
            result.message_id
        )

        return result

    except ApiException as e:
        logger.error("Erreur email annulation RDV %s", str(e))
        return None