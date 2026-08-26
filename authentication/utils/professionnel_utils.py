import random
import logging
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger(__name__)

# -----------------------------
# Générateur d'OTP
# -----------------------------
def generate_otp(length=6):
    """
    Génère un OTP numérique de `length` chiffres.
    Exemple : '482915'
    """
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


# -----------------------------
# Envoi email via Brevo (Sendinblue)
# -----------------------------
def send_register_notification_professionnel(email: str, nom_entreprise: str, otp: str):
    """
    Envoie un email de notification pour l'inscription d'un professionnel
    avec l'OTP généré.
    """
    try:
        # Configuration Brevo
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        # Contenu email
        email_data = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email, "name": nom_entreprise}],
            sender={
                "email": settings.DEFAULT_FROM_EMAIL,
                "name": settings.DEFAULT_FROM_NAME
            },
            subject="Création de votre compte professionnel",
            html_content=f"""
            <h3>Bonjour {nom_entreprise},</h3>

            <p>Votre compte professionnel a été créé avec succès sur <strong>Toorrii</strong>.</p>

            <p>Voici votre code de vérification (OTP) : <strong>{otp}</strong></p>

            <p>Vous devez utiliser ce code pour valider votre adresse email.</p>

            <br>
            <p>
                Cordialement,<br>
                <strong>L’équipe Toorrii</strong>
            </p>
            """
        )

        # Envoi de l'email
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

def send_reset_password_professionnel(email: str, nom_entreprise: str, otp: str):
    """
    Envoie un email de notification pour réinitialisation de mot de passe d'un professionnel
    avec l'OTP généré.
    """
    try:
        # Configuration Brevo
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        # Contenu email
        email_data = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email, "name": nom_entreprise}],
            sender={
                "email": settings.DEFAULT_FROM_EMAIL,
                "name": settings.DEFAULT_FROM_NAME
            },
            subject="Réinitialisation de mot de passe",
            html_content=f"""
            <h3>Bonjour {nom_entreprise},</h3>

            <p>Votre code de réinitialisation de mot de passe sur la platefome <strong>Toorrii</strong>.</p>

            <p>Voici votre code de vérification (OTP) : <strong>{otp}</strong></p>


            <br>
            <p>
                Cordialement,<br>
                <strong>L’équipe Toorrii</strong>
            </p>
            """
        )

        # Envoi de l'email
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




logger = logging.getLogger(__name__)

def send_reset_password_admin(email: str, nom: str, otp: str):
    """
    Envoie un email de notification pour réinitialisation de mot de passe d'un Admin
    avec l'OTP généré via Brevo.

    Args:
        email (str): Email de l'admin.
        nom (str): Nom de l'admin.
        otp (str): Code OTP de réinitialisation.

    Returns:
        sib_api_v3_sdk.SendSmtpEmail | None: Retour de l'API Brevo si succès, None sinon.

    Raises:
        ApiException: Si l'envoi échoue.
    """
    try:
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
            subject="Réinitialisation de mot de passe - Toorrii",
            html_content=f"""
                <h3>Bonjour {nom},</h3>
                <p>Vous avez demandé la réinitialisation de votre mot de passe sur la plateforme <strong>Toorrii</strong>.</p>
                <p>Voici votre code de vérification (OTP) : <strong>{otp}</strong></p>
                <p>Ce code est valable 15 minutes.</p>
                <br>
                <p>Cordialement,<br><strong>L’équipe Toorrii</strong></p>
            """
        )

        result = api_instance.send_transac_email(email_data)
        logger.info(
            "Email Admin envoyé à %s | Message ID: %s",
            email,
            getattr(result, "message_id", "N/A")
        )
        return result

    except ApiException as e:
        logger.error(
            "Erreur Brevo lors de l'envoi à %s | %s",
            email,
            str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Erreur inattendue lors de l'envoi de l'email à %s | %s",
            email,
            str(e)
        )
        raise