import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from faker import Faker
import os
from dotenv import load_dotenv
from .categorize import categorize_email  # Fonction pour catégoriser l'email selon son sujet ou son expéditeur
from .sentiment_analysis import analyze_sentiment  # Fonction pour analyser le sentiment de l'email

load_dotenv()


def send_random_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, priority="Normal"):
    """
    Envoie un email généré aléatoirement avec une priorité définie (Normal, Haute priorité, Basse priorité).
    L'email est analysé pour en extraire la catégorie et le sentiment.

    Args:
        smtp_server (str): Serveur SMTP.
        smtp_port (int): Port du serveur SMTP.
        sender_email (str): Email de l'expéditeur.
        sender_password (str): Mot de passe de l'expéditeur (ou mot de passe d'application).
        recipient_email (str): Email du destinataire.
        priority (str): Priorité de l'email (Normal, Haute priorité, Basse priorité).
    """

    faker = Faker()

    # Créer un message SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)

        # Générer l'email aléatoire
        for _ in range(3):  # Générer 3 emails pour tester
            msg = MIMEMultipart()

            # Générer le sujet et le corps
            subject = faker.sentence(nb_words=6)
            body = faker.paragraph(nb_sentences=5)

            # Ajouter l'analyse de sentiment et la catégorisation
            sentiment = analyze_sentiment(body)
            category = categorize_email(subject, sender_email)

            # Ajout d'une ligne de priorité dans le corps de l'email
            body += f"\n\nPriority: {priority}\nSentiment: {sentiment}\nCategory: {category}"

            # Construire l'email
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Ajouter le texte de l'email
            msg.attach(MIMEText(body, 'plain'))

            # Envoyer l'email
            server.send_message(msg)

            print(f"Email envoyé à {recipient_email} avec la priorité {priority} et la catégorie {category}")


# Utiliser les variables d'environnement pour les informations sensibles
send_random_email(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    sender_email=os.environ["GMAIL_EMAIL_ID"],
    sender_password=os.environ["EMAIL_APP_PASSWORD"],
    recipient_email=os.environ["OUTLOOK_EMAIL_ID"],
    priority="High"
)
