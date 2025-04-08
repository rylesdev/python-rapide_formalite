import imaplib
import os
import time
import email
import streamlit as st
from dotenv import load_dotenv
from lib.info import get_email_body
from lib.attachments import extract_attachments
from llm import return_ans
from lib.database import store_email  # Fonction pour stocker l'email dans la base de données
from lib.categorizer import categorize_email  # Fonction pour catégoriser l'email

# Charger les variables d'environnement
load_dotenv()

# Configurer la page Streamlit
st.set_page_config(
    page_title="Centralized Email Classifier",
    page_icon="📧",
)

st.write("# Welcome to the Centralized Email Classifier! 📧")

# Entrée des identifiants
email_id = st.text_input("Enter your Email ID (Gmail) which you want to monitor", placeholder="johndoe@example.com")
app_password = st.text_input("Enter your App Password (Gmail) to access the emails through IMAP",
                             placeholder="yourpassword")

monitor = st.button("Monitor")

if monitor and email_id and app_password:

    # Connexion au serveur IMAP du fournisseur de messagerie
    imap = imaplib.IMAP4_SSL(os.environ["GMAIL_IMAP_SERVER"], os.environ["GMAIL_IMAP_PORT"])
    imap.login(email_id, app_password)

    while True:
        # Sélectionner la boîte de réception
        imap.select('INBOX')
        typ, data = imap.search(None, '(UNSEEN)')

        if typ == 'OK':
            if len(data[0].split()) == 0:
                st.info("No new unseen message(s).", icon="ℹ️")
            else:
                st.success("New unread messages found!")

            for num in data[0].split():
                # Récupérer le message complet
                typ, msg_data = imap.fetch(num, '(RFC822)')

                if typ == 'OK':
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    subject = email_message['Subject']
                    sender = email_message['From']
                    body = get_email_body(email_message)

                    # Extraire les pièces jointes si elles existent
                    attachments = extract_attachments(email_message)

                    # Catégoriser l'email et déterminer l'équipe
                    category, team = categorize_email(subject, sender, body)

                    # Stocker l'email dans une base de données centralisée (ex: MongoDB, MySQL, etc.)
                    store_email(email_id, sender, subject, body, category, team, attachments)

                    # Afficher les informations sur l'email
                    with st.expander(f"Subject: {subject}"):
                        st.subheader("From:")
                        st.write(sender)

                        st.subheader("Subject:")
                        st.write(subject)

                        st.subheader("Body:")
                        st.write(body)

                        if attachments:
                            st.subheader("Attachments:")
                            for attachment in attachments:
                                st.write(attachment)

                        # Montrer l'équipe à laquelle l'email doit être envoyé
                        st.markdown(f'''
                            ## Team to which this mail should be forwarded to:
                            ```
                            {team}
                            ```
                        ''')

        # Attendre avant de vérifier de nouveaux emails
        with st.spinner('Checking for new emails...'):
            time.sleep(10)
