import ollama
from .categorize import categorize_email  # Une fonction pour catégoriser l'email
from .sentiment_analysis import analyze_sentiment  # Une fonction pour analyser le sentiment de l'email


def summarize_email(email_content: str, model: str = "qwen:1.8b", subject: str = "", sender: str = "") -> str:
    """
    Résume le contenu d'un email et ajoute des informations supplémentaires comme la catégorie et le sentiment.

    Args:
        email_content (str): Le contenu de l'email à résumer.
        model (str): Le modèle d'IA à utiliser pour générer le résumé. Par défaut, "qwen:1.8b".
        subject (str): Le sujet de l'email (facultatif, utilisé pour mieux adapter le résumé).
        sender (str): L'expéditeur de l'email (facultatif, utilisé pour mieux adapter le résumé).

    Returns:
        str: Le résumé de l'email avec des informations additionnelles comme la catégorie et le sentiment.
    """
    system_prompt = """
    Vous êtes un expert linguistique spécialisé dans les résumés concis et significatifs du contenu d'un email. 
    Générer un résumé clair et court du contenu de l'email que l'utilisateur peut lire rapidement pour comprendre 
    l'essentiel de l'email sans devoir le lire en entier.
    """

    # Catégoriser l'email avant de générer le résumé
    email_category = categorize_email(subject, sender)

    # Analyser le sentiment de l'email
    sentiment = analyze_sentiment(email_content)

    # Construire le message à envoyer à Ollama
    message = f"Subject: {subject}\nSender: {sender}\nCategory: {email_category}\nSentiment: {sentiment}\n\n"
    message += f"Email Content:\n{email_content}"

    # Créer la conversation avec Ollama
    stream = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        stream=True
    )

    # Construire la réponse
    summary = ""
    for chunk in stream:
        content = chunk["message"]["content"]
        summary += content

    # Retourner le résumé avec la catégorie et le sentiment
    return f"Summary:\n{summary.strip()}\n\nCategory: {email_category}\nSentiment: {sentiment}"

