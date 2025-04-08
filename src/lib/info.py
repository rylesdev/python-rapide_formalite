import imaplib
from email import message_from_bytes
from email.message import EmailMessage
from .database import \
    store_email  # Supposons que vous avez une fonction pour stocker les emails dans une base de données
from .categorize import categorize_email  # Supposons que vous avez une fonction pour catégoriser les emails
from .sentiment_analysis import \
    analyze_sentiment  # Supposons que vous avez une fonction pour analyser les sentiments des emails


def get_email_body(msg: EmailMessage) -> str:
    """
    Extrait le corps d'un message email.
    Retourne le corps du message en texte brut.
    """
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body += part.get_payload(decode=True).decode(part.get_content_charset())
    else:
        body = msg.get_payload(decode=True).decode(msg.get_content_charset())
    return body


def latest_email_message(imap_server, imap_port, email, password):
    """
    Récupère le dernier email d'un compte email spécifié en utilisant IMAP.

    Args:
        `imap_server` (str): Hôte du serveur IMAP
        `imap_port` (int): Numéro de port du serveur IMAP
        `email` (str): Adresse email
        `password` (str): Mot de passe de l'email (Mot de passe d'application pour Gmail)

    Retourne:
        email.message.EmailMessage: Le dernier message email.
    """
    # Se connecter au serveur IMAP
    imap = imaplib.IMAP4_SSL(imap_server, imap_port)
    imap.login(email, password)
    imap.select('INBOX')

    # Recherche du dernier email
    _, data = imap.search(None, 'ALL')
    email_ids = data[0].split()
    if not email_ids:
        print("Aucun email trouvé. La boîte de réception est vide.")
        return None

    latest_email_id = email_ids[-1]
    typ, data = imap.fetch(latest_email_id, '(RFC822)')
    raw_email = data[0][1]
    email_message = message_from_bytes(raw_email)

    imap.close()
    imap.logout()

    # Centraliser l'email
    centralize_email(email_message)

    return data, email_message


def centralize_email(email_message: EmailMessage):
    """
    Centralise un email en le stockant dans une base de données.

    Args:
        email_message (email.message.EmailMessage): L'email à centraliser.
    """
    subject = email_message['Subject']
    sender = email_message['From']
    body = get_email_body(email_message)

    # Catégoriser l'email (par exemple, en fonction du sujet ou de l'expéditeur)
    email_category = categorize_email(subject, sender)

    # Analyser le sentiment de l'email (optionnel)
    sentiment = analyze_sentiment(body)

    # Stocker l'email dans la base de données
    store_email(subject, sender, body, email_category, sentiment)


def get_ssb(mail: EmailMessage) -> tuple:
    """
    Extrait l'expéditeur, le sujet et le corps d'un email.

    Retourne: Tuple de l'expéditeur, du sujet et du corps
    """
    sender = mail['From']
    subject = mail['Subject']
    body = get_email_body(mail)

    return sender, subject, body


def RAWEmail(mail: EmailMessage) -> str:
    """
    Extrait l'email brut.

    Retourne: Email brut
    """
    return mail.decode('utf-8')

