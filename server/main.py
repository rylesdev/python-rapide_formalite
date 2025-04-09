import imaplib
import email
from email.header import decode_header

from src.info import extract_email_info, print_email_info

# Configuration IMAP
IMAP_SERVER = "imap.gmail.com"
EMAIL_ACCOUNT = "adresse_mail@gmail.com"
PASSWORD = "mot_de_passe"

# Dictionnaire de catégories pour les emails
CATEGORIES = {
    "Nouveaux Emails": ["nouveau", "urgent"],
    "En Cours": ["en cours", "suivi"],
    "Clos": ["clos", "terminé"],
    "Spam": ["spam", "promotion"]
}

def connect_to_mailbox():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, PASSWORD)
        mail.select("inbox")
        print("Connexion à la boîte mail réussie.")
        return mail
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return None

def fetch_emails(mail):
    status, messages = mail.search(None, "ALL")
    email_list = []

    if status != "OK":
        print("Impossible de récupérer les mails.")
        return []

    for num in messages[0].split():
        _, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Décode les infos
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

        email_list.append(email_data)

    return email_list

def categorize_email(subject, body):
    """
    Détermine la catégorie de l'email en fonction du sujet et du contenu.
    """
    subject = subject.lower()
    body = body.lower()

    for category, keywords in CATEGORIES.items():
        if any(keyword in subject or keyword in body for keyword in keywords):
            return category
    return "Non catégorisé"  # Si aucune catégorie ne correspond

def categorize_emails(emails):
    """
    Trie les emails en fonction de leur catégorie.
    """
    categories = {
        "Nouveaux Emails": [],
        "En Cours": [],
        "Clos": [],
        "Spam": [],
        "Non catégorisé": []
    }

    for mail in emails:
        category = categorize_email(mail.get("subject", ""), mail.get("body", ""))
        categories[category].append(mail)

    return categories

def main():
    mail = connect_to_mailbox()
    if not mail:
        return

    emails = fetch_emails(mail)
    if not emails:
        print("Aucun mail trouvé.")
        return

    print(f"{len(emails)} mails récupérés.\n")

    for e in emails:
        info = extract_email_info(e)
        print_email_info(info)

    print("\nTri des mails par catégorie...\n")
    categories = categorize_emails(emails)

    for category, mails in categories.items():
        print(f"{len(mails)} mail(s) dans la catégorie : {category}")
        for mail in mails:
            print(f"  - {mail['subject']}")

if __name__ == "__main__":
    main()
