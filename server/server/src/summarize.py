def summarize_email(body, max_length=200, category="Nouveaux Emails"):
    """
    Résume le contenu d'un email en limitant le nombre de caractères.

    Ajoute également la catégorie de l'email dans le résumé.

    :param body: Le contenu complet de l'email.
    :param max_length: Le nombre maximum de caractères du résumé.
    :param category: La catégorie de l'email.
    :return: Une version abrégée du contenu de l'email avec la catégorie.
    """
    if not body:
        return f"Aucun contenu à afficher. Catégorie : {category}"

    body = body.strip().replace("\n", " ").replace("\r", " ")
    summary = body[:max_length]

    if len(body) > max_length:
        summary += "..."

    return f"{summary} (Catégorie : {category})"
