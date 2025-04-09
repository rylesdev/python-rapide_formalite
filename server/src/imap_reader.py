import imaplib
import email
from email.header import decode_header
import json


def connect_to_mailbox(imap_server, email_account, password):
    """
    Connecte à la boîte mail via IMAP.
    """
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_account, password)
        mail.select("inbox")
        print("Connexion à la boîte mail réussie.")
        return mail
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return None


def fetch_emails(mail):
    """
    Récupère tous les emails de la boîte de réception et les trie par statut.
    """
    status, messages = mail.search(None, "ALL")
    email_list = {
        "Nouveaux Emails": [],
        "En Cours": [],
        "Clos": [],
        "Spam": [],
        "Priorité Haute": [],
        "Emails Personnels": [],
        "Emails Professionnels": []
    }

    if status != "OK":
        print("Impossible de récupérer les mails.")
        return {}

    for num in messages[0].split():
        _, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Décode les infos de l'email
        subject, encoding = decode_header(msg.get("Subject"))[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")

        from_ = msg.get("From")
        date_ = msg.get("Date")

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        email_data = {
            "from": from_,
            "subject": subject,
            "date": date_,
            "body": body
        }

        # Trier les emails en fonction de leur statut
        # Par exemple, ici, on pourrait décider manuellement du statut ou utiliser des règles (e.g., mots-clés dans l'objet ou l'expéditeur).

        if "Urgent" in subject:
            email_list["Priorité Haute"].append(email_data)
        elif "Spam" in subject:
            email_list["Spam"].append(email_data)
        elif "Personnel" in subject:
            email_list["Emails Personnels"].append(email_data)
        elif "Professionnel" in subject:
            email_list["Emails Professionnels"].append(email_data)
        else:
            email_list["Nouveaux Emails"].append(email_data)

    return email_list


def save_emails_to_storage(emails, filepath="server/data/output.json"):
    """
    Sauvegarde les emails dans un fichier JSON, en les triant par catégorie.
    """
    try:
        # Charger les emails existants dans le fichier JSON, si nécessaire
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                stored_emails = json.load(file)
        except FileNotFoundError:
            stored_emails = []

        # Ajouter les nouveaux emails à la liste existante
        stored_emails.append(emails)

        # Sauvegarder les emails dans le fichier
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(stored_emails, file, indent=4, ensure_ascii=False)

        print("Emails sauvegardés avec succès.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des emails : {e}")
