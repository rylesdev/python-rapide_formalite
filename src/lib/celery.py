from celery import Celery
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import decode_header
from email.message import EmailMessage
from email import message_from_string
from lib.summarize import summarize_email
from lib.forward import decode_subject

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Configuration de l'application Celery
celery_app = Celery('tasks', broker='pyamqp://guest@localhost//')

# URL de redirection et du logo à inclure dans les emails
REDIRECT_URL = "http://localhost:3000"
LOGO_URL = "https://i.ibb.co/P60gmv3/EC-Footer-small.png"


# Fonction de transfert d'email avec tri selon la catégorie
@celery_app.task
def forward_email_and_sort(email_message: EmailMessage, smtp_server: str, smtp_port: int, smtp_email: str,
                           smtp_password: str, forward_to: str, email_category: str, cc_to: list = [],
                           bcc_to: list = [], sentiment="") -> None:
    """
    Transfère un message email à un destinataire spécifié et l'ajoute à la catégorie appropriée dans le système de gestion des emails.

    Args:
        email_message (email.message.EmailMessage): L'email à transférer.
        smtp_server (str): Le serveur SMTP pour l'envoi de l'email.
        smtp_port (int): Le port SMTP.
        smtp_email (str): L'email de l'expéditeur.
        smtp_password (str): Le mot de passe de l'expéditeur.
        forward_to (str): L'adresse email du destinataire.
        email_category (str): La catégorie de l'email à trier (ex. "Nouveaux Emails", "En Cours", "Clos", etc.).
    """
    email_message = message_from_string(email_message)

    # Création d'un nouveau message pour le transfert
    forwarded_email = MIMEMultipart()
    forwarded_email['From'] = smtp_email
    forwarded_email['To'] = forward_to
    if cc_to:
        forwarded_email['CC'] = ', '.join(cc_to)
    forwarded_email[
        'Subject'] = f"{decode_subject(email_message['Subject'])} - ({sentiment}) Fwd from EC"  # EC = Email Classifier

    html_part = None
    # Traitement de chaque partie de l'email (textes, pièces jointes, etc.)
    for part in email_message.walk():
        if part.get_content_type() == 'text/html':
            html_part = part.get_payload(decode=True).decode(part.get_content_charset())
        elif part.get_content_disposition() == 'attachment':
            # Ajout des pièces jointes
            new_part = MIMEBase(part.get_content_type().split('/')[0], part.get_content_type().split('/')[1])
            new_part.set_payload(part.get_payload(decode=True))
            encoders.encode_base64(new_part)
            new_part.add_header('Content-Disposition', 'attachment', filename=part.get_filename())
            forwarded_email.attach(new_part)
        else:
            continue

    # Résumé de l'email à transférer
    summary = summarize_email(
        html_part if html_part else email_message.get_payload(decode=True).decode(email_message.get_content_charset()))
    forwarded_email.attach(MIMEText(f"Email Summary:\n{summary}\n\n", 'plain'))

    if html_part:
        forwarded_email.attach(MIMEText(html_part, 'html'))
    else:
        # Si la partie HTML n'existe pas, utiliser du texte brut
        text_part = email_message.get_payload(decode=True).decode(email_message.get_content_charset())
        forwarded_email.attach(MIMEText(text_part, 'plain'))

    # Ajouter un lien avec le logo dans l'email
    html_string = f"""
    <div style="margin: 0 auto; width: 50%;">
        <a href="{REDIRECT_URL}">
            <img src="{LOGO_URL}" alt="Logo" style="display: block; margin: 0 auto;">
        </a>
    </div>
    """
    forwarded_email.attach(MIMEText(html_string, 'html'))

    # Connexion au serveur SMTP et envoi de l'email
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_email, smtp_password)
        smtp.send_message(
            forwarded_email,
            to_addrs=[forward_to] + (cc_to or []) + (bcc_to or [])
        )

    # Une fois l'email transféré, trié, vous pouvez ajouter l'email à la bonne catégorie dans le système de gestion
    # (Vous devrez gérer cela avec votre logique de gestion des catégories d'email dans votre système)

    # Exemple d'ajout de l'email à une catégorie spécifique dans votre structure JSON :
    add_email_to_category(email_message, email_category)


def add_email_to_category(email_message, email_category):
    """
    Ajoute l'email à la catégorie spécifiée dans la structure de gestion des emails.

    Args:
        email_message (email.message.EmailMessage): L'email à ajouter.
        email_category (str): La catégorie dans laquelle ajouter l'email.
    """
    # Ceci est un exemple de la manière dont vous pourriez structurer l'ajout d'email à une catégorie
    categories = {
        "Nouveaux Emails": [],
        "En Cours": [],
        "Clos": [],
        "Spam": [],
        "Priorité Haute": [],
        "Emails Personnels": [],
        "Emails Professionnels": []
    }

    # Vous devrez récupérer la catégorie spécifique du fichier JSON et ajouter l'email
    if email_category in categories:
        categories[email_category].append(email_message)
        print(f"Email ajouté à la catégorie : {email_category}")
    else:
        print(f"Catégorie {email_category} non trouvée.")
