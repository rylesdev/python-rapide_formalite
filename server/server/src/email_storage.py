import json

def save_emails_to_storage(emails, filepath="server/data/output.json"):
    """
    Sauvegarde les emails dans un fichier JSON.
    Chaque email sera sauvegardé avec son statut actuel : 'Nouveau', 'En cours', 'Clos'.
    Si le fichier existe déjà, il sera mis à jour avec les nouveaux emails.
    """

    try:
        # Charger les emails existants dans le fichier JSON, si nécessaire
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                stored_emails = json.load(file)
        except FileNotFoundError:
            stored_emails = []

        # Ajouter les nouveaux emails à la liste existante avec leur statut
        for email in emails:
            # Ajouter un statut par défaut si ce n'est pas déjà présent
            if "status" not in email:
                email["status"] = "Nouveau"  # Par défaut, un email est "Nouveau"
            stored_emails.append(email)

        # Sauvegarder les emails dans le fichier
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(stored_emails, file, indent=4, ensure_ascii=False)

        print("Emails sauvegardés avec succès.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des emails : {e}")
