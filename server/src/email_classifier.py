def classify_email(email):
    """
    Classe un email selon son statut : 'Nouveau', 'En cours', 'Clos'
    L'état d'un email peut être basé sur des critères comme :
    - La présence d'un mot-clé spécifique (ex: "réponse" pour "En cours")
    - La date de réception (les emails plus anciens pourraient être classés "Clos")
    - La présence de certaines actions ou réponses
    """

    # Extraire les informations de l'email
    subject = email.get("subject", "").lower()
    body = email.get("body", "").lower()

    # Critères basés sur des mots-clés (modifiables selon tes besoins)
    in_progress_keywords = ["réponse", "en cours", "suivi", "en attente"]
    closed_keywords = ["fermé", "clos", "terminé", "résolu"]
    new_keywords = ["nouveau", "urgent", "demandé", "reçu"]

    # Vérification pour "En cours"
    for keyword in in_progress_keywords:
        if keyword in subject or keyword in body:
            return "En cours"

    # Vérification pour "Clos"
    for keyword in closed_keywords:
        if keyword in subject or keyword in body:
            return "Clos"

    # Vérification pour "Nouveau"
    for keyword in new_keywords:
        if keyword in subject or keyword in body:
            return "Nouveau"

    # Si aucun critère n'est trouvé, l'email est classé comme "Nouveau" par défaut
    return "Nouveau"
