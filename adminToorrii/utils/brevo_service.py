import logging
from django.conf import settings

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)


def send_professionnel_notification(email: str, nom: str):
    """
    Envoie un email de notification via Brevo (Sendinblue)
    """

    # -----------------------------
    # Configuration Brevo
    # -----------------------------
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # -----------------------------
    # Contenu email
    # -----------------------------
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email, "name": nom}],
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": settings.DEFAULT_FROM_NAME
        },
        subject="Création de votre compte professionnel",
        html_content=f"""
        <h3>Bonjour {nom},</h3>

        <p>Votre compte professionnel a été créé avec succès
        par l'administration <strong>Toorrii</strong>.</p>

        <p>Vous pouvez maintenant accéder à la plateforme.</p>

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
            "Email Brevo envoyé à %s | Message ID: %s",
            email,
            result.message_id
        )
        return result

    except ApiException as e:
        logger.error(
            "Erreur Brevo lors de l'envoi à %s | %s",
            email,
            str(e)
        )
        raise e


def send_register_notification_professionnel_par_admin(email: str, nom: str):
    """
    Envoie un email de notification via Brevo (Sendinblue)
    """

    # -----------------------------
    # Configuration Brevo
    # -----------------------------
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # -----------------------------
    # Contenu email
    # -----------------------------
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email, "name": nom}],
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": settings.DEFAULT_FROM_NAME
        },
        subject="Création de votre compte professionnel",
        html_content=f"""
        <h3>Bonjour {nom},</h3>

        <p>Votre compte professionnel a été créé avec succès
        par l'administration <strong>Toorrii</strong>.</p>

        <p>Vous pouvez maintenant accéder à la plateforme.</p>

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
            "Email Brevo envoyé à %s | Message ID: %s",
            email,
            result.message_id
        )
        return result

    except ApiException as e:
        logger.error(
            "Erreur Brevo lors de l'envoi à %s | %s",
            email,
            str(e)
        )
        raise e

def send_professionnel_notification_activation(email: str, nom: str):
    """
    Envoie un email de notification via Brevo (Sendinblue)
    """

    # -----------------------------
    # Configuration Brevo
    # -----------------------------
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # -----------------------------
    # Contenu email
    # -----------------------------
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email, "name": nom}],
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": settings.DEFAULT_FROM_NAME
        },
        subject="Activation de votre compte professionnel",
        html_content=f"""
        <h3>Bonjour {nom},</h3>

        <p>Votre compte professionnel a été activé
        par l'administration <strong>Toorrii</strong>.</p>

        <p>Vous pouvez maintenant accéder à la plateforme.</p>

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
            "Email Brevo envoyé à %s | Message ID: %s",
            email,
            result.message_id
        )
        return result

    except ApiException as e:
        logger.error(
            "Erreur Brevo lors de l'envoi à %s | %s",
            email,
            str(e)
        )
        raise e        

def send_professionnel_notification_désactivation(email: str, nom: str):
    """
    Envoie un email de notification via Brevo (Sendinblue)
    """

    # -----------------------------
    # Configuration Brevo
    # -----------------------------
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # -----------------------------
    # Contenu email
    # -----------------------------
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email, "name": nom}],
        sender={
            "email": settings.DEFAULT_FROM_EMAIL,
            "name": settings.DEFAULT_FROM_NAME
        },
        subject="Désactivation de votre compte professionnel",
        html_content=f"""
        <h3>Bonjour {nom},</h3>

        <p>Votre compte professionnel a été désactivé
        par l'administration <strong>Toorrii</strong>.</p>


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
            "Email Brevo envoyé à %s | Message ID: %s",
            email,
            result.message_id
        )
        return result

    except ApiException as e:
        logger.error(
            "Erreur Brevo lors de l'envoi à %s | %s",
            email,
            str(e)
        )
        raise e        

def send_professionnel_demande_désactivation_compte(email: str, nom: str):
    """
    Envoie un email à l'administration Toorrii pour demander la désactivation
    du compte d'un professionnel. L'expéditeur est l'utilisateur.
    """

    # -----------------------------
    # Configuration Brevo
    # -----------------------------
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # -----------------------------
    # Contenu email
    # -----------------------------
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": settings.DEFAULT_FROM_EMAIL, "name": "Administration Toorrii"}],  # Receveur = admin
        sender={
            "email": email,       # Expéditeur = utilisateur
            "name": nom
        },
        subject="Demande de désactivation de compte professionnel",
        html_content=f"""
        <h3>Bonjour Toorrii,</h3>

        <p>Le professionnel <strong>{nom}</strong> ({email}) a demandé la désactivation de son compte.</p>

        <p>Merci de traiter cette demande dans les plus brefs délais.</p>

        <br>
        <p>
            Cordialement,<br>
            <strong>Plateforme Toorrii</strong>
        </p>
        """
    )

    try:
        result = api_instance.send_transac_email(email_data)
        logger.info(
            "Email Brevo envoyé à l'administration depuis %s | Message ID: %s",
            email,
            result.message_id
        )
        return result

    except ApiException as e:
        logger.error(
            "Erreur Brevo lors de l'envoi à l'administration depuis %s | %s",
            email,
            str(e)
        )
        raise e    