def extract_email_info(email_obj):
    """
    Extrait les informations principales d'un email.
    email_obj doit être un dictionnaire contenant les champs suivants :
    - from
    - subject
    - date
    - body
    """
    # Catégorisation des emails basés sur des critères spécifiques
    category = "Nouveaux Emails"  # Valeur par défaut

    if "Urgent" in email_obj.get("subject", ""):
        category = "Priorité Haute"
    elif "Spam" in email_obj.get("subject", ""):
        category = "Spam"
    elif "Personnel" in email_obj.get("subject", ""):
        category = "Emails Personnels"
    elif "Professionnel" in email_obj.get("subject", ""):
        category = "Emails Professionnels"

    # Retourner les informations extraites de l'email, avec la catégorie ajoutée
    return {
        "Expéditeur": email_obj.get("from", "Inconnu"),
        "Objet": email_obj.get("subject", "Sans objet"),
        "Date": email_obj.get("date", "Date inconnue"),
        "Aperçu": email_obj.get("body", "")[:100] + "...",  # Les 100 premiers caractères
        "Catégorie": category  # Ajout de la catégorie
    }


def print_email_info(email_info):
    """
    Affiche joliment les informations d’un mail pour debug ou affichage.
    """
    print("📧 Email reçu :")
    print(f"  Expéditeur : {email_info['Expéditeur']}")
    print(f"  Objet      : {email_info['Objet']}")
    print(f"  Date       : {email_info['Date']}")
    print(f"  Aperçu     : {email_info['Aperçu']}")
    print(f"  Catégorie  : {email_info['Catégorie']}")  # Affiche la catégorie de l'email
    print("-" * 50)
