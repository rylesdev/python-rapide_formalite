import imaplib
import os
import time
import email
import streamlit as st
from dotenv import load_dotenv
from lib.info import obtenir_corps_email
from lib.attachments import extraire_pieces_jointes
from llm import retourner_reponse
from lib.database import stocker_email  # Fonction pour stocker l'email dans la base de données
from lib.categorizer import categoriser_email  # Fonction pour catégoriser l'email

# Charger les variables d'environnement
load_dotenv()

# Configurer la page Streamlit
st.set_page_config(
    page_title="Classificateur Centralisé d'Emails",
    page_icon="📧",
)

st.write("# Bienvenue dans le Classificateur Centralisé d'Emails ! 📧")

# Saisie des identifiants
email_utilisateur = st.text_input("Entrez votre adresse email (Gmail) à surveiller", placeholder="johndoe@exemple.com")
mot_de_passe_app = st.text_input("Entrez votre Mot de Passe d'Application (Gmail) pour accéder aux emails via IMAP",
                             placeholder="votremotdepasse")

surveiller = st.button("Surveiller")

if surveiller and email_utilisateur and mot_de_passe_app:

    # Connexion au serveur IMAP
    imap = imaplib.IMAP4_SSL(os.environ["GMAIL_IMAP_SERVER"], os.environ["GMAIL_IMAP_PORT"])
    imap.login(email_utilisateur, mot_de_passe_app)

    while True:
        # Sélectionner la boîte de réception
        imap.select('INBOX')
        typ, data = imap.search(None, '(UNSEEN)')  # Emails non lus

        if typ == 'OK':
            if len(data[0].split()) == 0:
                st.info("Aucun nouveau message non lu.", icon="ℹ️")
            else:
                st.success("Nouveaux messages non lus trouvés !")

            for num in data[0].split():
                # Récupérer le message complet
                typ, msg_data = imap.fetch(num, '(RFC822)')

                if typ == 'OK':
                    email_brut = msg_data[0][1]
                    message_email = email.message_from_bytes(email_brut)
                    sujet = message_email['Subject']
                    expediteur = message_email['From']
                    corps = obtenir_corps_email(message_email)

                    # Extraire les pièces jointes si elles existent
                    pieces_jointes = extraire_pieces_jointes(message_email)

                    # Catégoriser l'email et déterminer l'équipe
                    categorie, equipe = categoriser_email(sujet, expediteur, corps)

                    # Stocker l'email dans la base de données
                    stocker_email(email_utilisateur, expediteur, sujet, corps, categorie, equipe, pieces_jointes)

                    # Afficher les détails de l'email
                    with st.expander(f"Sujet : {sujet}"):
                        st.subheader("Expéditeur :")
                        st.write(expediteur)

                        st.subheader("Sujet :")
                        st.write(sujet)

                        st.subheader("Corps :")
                        st.write(corps)

                        if pieces_jointes:
                            st.subheader("Pièces jointes :")
                            for piece in pieces_jointes:
                                st.write(piece)

                        # Afficher l'équipe destinataire
                        st.markdown(f'''
                            ## Équipe à laquelle transférer cet email :
                            ```
                            {equipe}
                            ```
                        ''')

        # Attendre avant la prochaine vérification
        with st.spinner('Vérification de nouveaux emails...'):
            time.sleep(10)  # Toutes les 10 secondes