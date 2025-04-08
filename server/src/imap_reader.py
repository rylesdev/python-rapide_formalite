import imaplib
import os
import time
import email
import streamlit as st
from dotenv import load_dotenv
from lib.info import extraire_corps_email
from lib.attachments import extraire_pieces_jointes
from llm import obtenir_reponse
from lib.database import stocker_email  # Fonction pour stocker l'email dans la base de données
from lib.categorizer import categoriser_email  # Fonction pour catégoriser l'email

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Classificateur Centralisé d'Emails",
    page_icon="📧",
)

st.write("# Bienvenue dans le Classificateur Centralisé d'Emails ! 📧")

# Section d'authentification
adresse_email = st.text_input("Entrez votre adresse Gmail à surveiller",
                              placeholder="exemple@gmail.com")
mot_de_passe_app = st.text_input("Entrez votre mot de passe d'application Gmail pour l'accès IMAP",
                                 placeholder="votre_mot_de_passe",
                                 type="password")

bouton_surveillance = st.button("Démarrer la surveillance")

if bouton_surveillance and adresse_email and mot_de_passe_app:
    # Connexion au serveur IMAP
    try:
        imap = imaplib.IMAP4_SSL(os.environ["GMAIL_IMAP_SERVER"],
                                 os.environ["GMAIL_IMAP_PORT"])
        imap.login(adresse_email, mot_de_passe_app)
        st.success("Connexion IMAP réussie !")

        while True:
            # Sélection de la boîte de réception
            imap.select('INBOX')
            status, donnees = imap.search(None, '(UNSEEN)')  # Emails non lus

            if status == 'OK':
                if len(donnees[0].split()) == 0:
                    st.info("Aucun nouveau message non lu.", icon="ℹ️")
                else:
                    st.success(f"{len(donnees[0].split())} nouveau(x) message(s) non lu(s) trouvé(s) !")

                for num_msg in donnees[0].split():
                    # Récupération du message
                    status, msg_data = imap.fetch(num_msg, '(RFC822)')

                    if status == 'OK':
                        email_brut = msg_data[0][1]
                        message = email.message_from_bytes(email_brut)
                        sujet = message['Subject']
                        expediteur = message['From']
                        corps = extraire_corps_email(message)

                        # Extraction des pièces jointes
                        pieces_jointes = extraire_pieces_jointes(message)

                        # Catégorisation de l'email
                        categorie, equipe = categoriser_email(sujet, expediteur, corps)

                        # Stockage en base de données
                        stocker_email(adresse_email, expediteur, sujet, corps,
                                      categorie, equipe, pieces_jointes)

                        # Affichage des détails
                        with st.expander(f"📨 {sujet}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Expéditeur:**")
                                st.write(expediteur)
                            with col2:
                                st.markdown("**Catégorie:**")
                                st.code(categorie)

                            st.markdown("**Contenu:**")
                            st.write(corps)

                            if pieces_jointes:
                                st.markdown("**Pièces jointes:**")
                                for piece in pieces_jointes:
                                    st.write(f"📎 {piece}")

                            st.markdown(f"**Équipe destinataire:**")
                            st.info(equipe, icon="👥")

            # Pause entre les vérifications
            with st.spinner('Vérification des nouveaux emails dans 10 secondes...'):
                time.sleep(10)

    except Exception as e:
        st.error(f"Erreur de connexion : {str(e)}")