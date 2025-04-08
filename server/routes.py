from flask import Flask, jsonify, request
from imap_reader import connect_to_mailbox, fetch_emails
from email_classifier import classify_email
from email_storage import store_email_data
from summarize import summarize_email

app = Flask(__name__)

# Configuration IMAP
IMAP_SERVER = "imap.example.com"
EMAIL_ACCOUNT = "tonemail@example.com"
PASSWORD = "tonMotDePasse"

# Dictionnaire des catégories d'emails
CATEGORIES = {
    "Nouveaux Emails": ["nouveau", "urgent"],
    "En Cours": ["en cours", "suivi"],
    "Clos": ["clos", "terminé"],
    "Spam": ["spam", "promotion"]
}

@app.route('/fetch-emails', methods=['GET'])
def get_emails():
    """
    Endpoint pour récupérer les emails.
    """
    mail = connect_to_mailbox(IMAP_SERVER, EMAIL_ACCOUNT, PASSWORD)
    if not mail:
        return jsonify({"error": "Erreur de connexion à la boîte de réception"}), 500

    emails = fetch_emails(mail)
    if not emails:
        return jsonify({"message": "Aucun email trouvé"}), 404

    categorized_emails = categorize_emails(emails)
    return jsonify(categorized_emails), 200

@app.route('/classify-email', methods=['POST'])
def classify_single_email():
    """
    Endpoint pour classifier un email spécifique en fonction de son contenu.
    """
    email_data = request.json
    if not email_data or 'subject' not in email_data or 'body' not in email_data:
        return jsonify({"error": "Données manquantes dans la requête"}), 400

    subject = email_data.get('subject')
    body = email_data.get('body')

    category = classify_email(subject, body)
    return jsonify({"category": category}), 200

@app.route('/store-email', methods=['POST'])
def store_email():
    """
    Endpoint pour stocker les données d'un email dans une base de données ou un fichier.
    """
    email_data = request.json
    if not email_data:
        return jsonify({"error": "Aucune donnée d'email fournie"}), 400

    try:
        store_email_data(email_data)
        return jsonify({"message": "Email stocké avec succès"}), 201
    except Exception as e:
        return jsonify({"error": f"Erreur lors du stockage : {e}"}), 500

@app.route('/summarize-email', methods=['POST'])
def summarize_single_email():
    """
    Endpoint pour obtenir un résumé d'un email.
    """
    email_data = request.json
    if not email_data or 'subject' not in email_data or 'body' not in email_data:
        return jsonify({"error": "Données manquantes dans la requête"}), 400

    subject = email_data.get('subject')
    body = email_data.get('body')

    summary = summarize_email(subject, body)
    return jsonify({"summary": summary}), 200

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

if __name__ == '__main__':
    app.run(debug=True)
