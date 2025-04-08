import PyPDF2
import os

# Fonction pour extraire les pièces jointes et les trier
def extract_attachments_and_sort(email_message, email_category):
    extracted_texts = []

    # Parcours des différentes parties de l'email
    for part in email_message.walk():
        if part.get_content_disposition() == 'attachment':
            # Sauvegarde de la pièce jointe dans un fichier local
            filename = part.get_filename()
            with open(filename, 'wb') as f:
                f.write(part.get_payload(decode=True))

            # Extraction du texte si le fichier est un PDF
            file_extension = os.path.splitext(filename)[1]

            if file_extension == '.pdf':
                # Extraction du texte depuis le fichier PDF
                pdf_file_obj = open(filename, 'rb')
                pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
                text = ''
                for page_num in range(len(pdf_reader.pages)):
                    page_obj = pdf_reader.pages[page_num]
                    text += page_obj.extract_text()
                pdf_file_obj.close()
            else:
                text = None

            # Suppression du fichier temporaire
            os.remove(filename)

            # Ajout du texte extrait à la liste, si applicable
            if text is not None:
                extracted_texts.append(text)

    # En fonction de la catégorie de l'email, vous pouvez ajouter l'extraction de texte
    # à l'email correspondant dans votre structure de données

    # Exemple de tri selon la catégorie (vous devrez probablement ajuster la logique selon votre projet)
    if email_category == "Nouveaux Emails":
        # Ajoutez les textes extraits à la liste des nouveaux emails
        # Par exemple, vous pouvez ajouter les textes extraits dans une liste spécifique à cette catégorie
        pass
    elif email_category == "En Cours":
        # Ajoutez les textes extraits à la liste des emails en cours
        pass
    elif email_category == "Clos":
        # Ajoutez les textes extraits à la liste des emails clos
        pass
    elif email_category == "Spam":
        # Ajoutez les textes extraits à la liste des emails spam
        pass
    elif email_category == "Priorité Haute":
        # Ajoutez les textes extraits à la liste des emails avec priorité haute
        pass
    elif email_category == "Emails Personnels":
        # Ajoutez les textes extraits à la liste des emails personnels
        pass
    elif email_category == "Emails Professionnels":
        # Ajoutez les textes extraits à la liste des emails professionnels
        pass

    return extracted_texts
