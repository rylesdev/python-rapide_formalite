import smtplib
import os
from dotenv import load_dotenv

load_dotenv()
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import decode_header
from email.message import EmailMessage
from .summarize import summarize_email

# Ajouter une logique pour centraliser et trier les emails
from .database import \
    store_email  # Supposons que vous avez une fonction pour stocker les emails dans une base de données

REDIRECT_URL = "http://localhost:3000"
LOGO_URL = "https://i.ibb.co/P60gmv3/EC-Footer-small.png"


def decode_subject(subject):
    """
    Décoder le sujet d'un email.
    """
    decoded = decode_header(subject)
    decoded_subject = []
    for part, encoding in decoded:
        if isinstance(part, bytes):
            decoded_subject.append(part.decode(encoding or 'utf-8'))
        else:
            decoded_subject.append(part)
    return ''.join(decoded_subject)


def centralize_email(email_message: EmailMessage):
    """
    Centralise un email en le stockant dans une base de données ou un autre système.

    Args:
        email_message (email.message.EmailMessage): L'email à centraliser.
    """
    subject = decode_subject(email_message['Subject'])
    sender = email_message['From']
    body = email_message.get_payload(decode=True).decode(email_message.get_content_charset())

    # Ajoutez une logique pour trier ou classer l'email (par exemple en fonction de l'objet, de l'expéditeur, etc.)
    email_category = categorize_email(subject, sender)  # Supposons que cette fonction existe

    # Stockage de l'email dans la base de données (exemple fictif)
    store_email(subject, sender, body, email_category)


def forward_email(email_message: EmailMessage, smtp_server: str, smtp_port: int, smtp_email: str, smtp_password: str,
                  forward_to: str, cc_to: list = [], bcc_to: list = [], sentiment="") -> None:
    """
    Transférer un email à un destinataire tout en maintenant la mise en forme du message d'origine.

    Args:
        email_message (email.message.EmailMessage): L'email à transférer.
        smtp_server (str): L'hôte du serveur SMTP.
        smtp_port (int): Le port du serveur SMTP.
        smtp_email (str): L'email de l'expéditeur.
        smtp_password (str): Le mot de passe de l'expéditeur.
        forward_to (str): L'email du destinataire.
    """
    # Centralisation de l'email avant de le transférer
    centralize_email(email_message)

    # Créer un nouvel email pour le transfert
    forwarded_email = MIMEMultipart()
    forwarded_email['From'] = smtp_email
    forwarded_email['To'] = forward_to
    if cc_to:
        forwarded_email['CC'] = ', '.join(cc_to)
    forwarded_email['Subject'] = f"{decode_subject(email_message['Subject'])} - ({sentiment}) Fwd from EC"

    html_part = None
    for part in email_message.walk():
        if part.get_content_type() == 'text/html':
            html_part = part.get_payload(decode=True).decode(part.get_content_charset())
        elif part.get_content_disposition() == 'attachment':
            # Gérer les pièces jointes
            new_part = MIMEBase(part.get_content_type().split('/')[0], part.get_content_type().split('/')[1])
            new_part.set_payload(part.get_payload(decode=True))
            encoders.encode_base64(new_part)
            new_part.add_header('Content-Disposition', 'attachment', filename=part.get_filename())
            forwarded_email.attach(new_part)
        else:
            continue

    try:
        summary = summarize_email(html_part if html_part else email_message.get_payload(decode=True).decode(
            email_message.get_content_charset()))
        summary_html = f"<p style='font-size: 1.2em; font-weight: bold; font-style: italic;'>Email Summary:<br>{summary}</p>"
        forwarded_email.attach(MIMEText(summary_html, 'html'))
    except:
        pass

    if html_part:
        forwarded_email.attach(MIMEText(html_part, 'html'))
    else:
        # Si la partie HTML n'est pas trouvée, utilisez le texte brut
        text_part = email_message.get_payload(decode=True).decode(email_message.get_content_charset())
        forwarded_email.attach(MIMEText(text_part, 'plain'))

    # Ajouter une image ou une signature à l'email
    html_string = f"""
    <div style="margin: 0 auto; width: 50%;">
        <a href="{REDIRECT_URL}">
            <img src="{LOGO_URL}" alt="Barclays Logo" style="display: block; margin: 0 auto;">
        </a>
    </div>
    """
    forwarded_email.attach(MIMEText(html_string, 'html'))

    # Connexion au serveur SMTP pour envoyer l'email
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_email, smtp_password)
        smtp.send_message(
            forwarded_email,
            to_addrs=[forward_to] + (cc_to or []) + (bcc_to or [])
        )
