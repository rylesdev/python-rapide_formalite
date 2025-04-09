from haystack import Document, Pipeline
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack.components.preprocessors import DocumentCleaner
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore
from json import loads
from lib.database import stocker_email  # Fonction pour stocker les emails
from lib.categorizer import categoriser_email  # Fonction pour catégoriser les emails

# Chargement des données JSON pour le RAG
with open('src/data/mail.json', 'r') as fichier:
    donnees = loads(fichier.read())

# Conversion des données JSON en documents Haystack
documents = []
for noeud in donnees['nodes']:
    documents.append(Document(content=str(noeud)))

# Nettoyage des documents
nettoyeur = DocumentCleaner()
documents_propres = nettoyeur.run(documents=documents)

# Création du magasin de documents en mémoire
magasin_documents = InMemoryDocumentStore()
magasin_documents.write_documents(documents_propres['documents'])

# Configuration du récupérateur BM25
recuperateur = InMemoryBM25Retriever(document_store=magasin_documents, top_k=1)

# Modèle de prompt pour le système RAG
modele_prompt = '''
En tant que responsable de la distribution des emails, votre tâche est de diriger les messages vers les bons destinataires.
Utilisez le contexte fourni pour déterminer le(s) destinataire(s) le(s) plus approprié(s) pour la requête.
Le contexte inclut la structure organisationnelle, les départements et les équipes.
Vous pouvez aussi utiliser le tag "description" du contexte pour faire correspondre le sens sémantique de l'email.
Votre réponse doit être l'id de l'équipe (nœud feuille) à qui la requête doit être adressée.

Contexte: 
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Requête: {{ query }}
Merci de répondre dans le format suivant: <x>
où 'x' est l'id du nœud feuille.
Votre réponse ne doit contenir QUE L'ID
'''

# Construction des composants du pipeline
constructeur_prompt = PromptBuilder(template=modele_prompt)

# Configuration du générateur Ollama (modèle Qwen 4b)
generateur = OllamaGenerator(
    model="qwen:4b",
    url="http://localhost:11434",
    parametres_generation={
        "num_predict": 100,
        "temperature": 0.9,
    },
)

# Construction du pipeline RAG
pipeline_rag = Pipeline()
pipeline_rag.add_component("recuperateur", recuperateur)
pipeline_rag.add_component("constructeur_prompt", constructeur_prompt)
pipeline_rag.add_component("modele_llm", generateur)
pipeline_rag.connect("recuperateur", "constructeur_prompt.documents")
pipeline_rag.connect("constructeur_prompt", "modele_llm")


def obtenir_reponse(requete):
    try:
        resultat = pipeline_rag.run({
            "constructeur_prompt": {"query": requete},
            "recuperateur": {"query": requete}
        })
        print(resultat)
        reponse = {
            "equipe": resultat['modele_llm']['replies'][0].strip()
        }
        return reponse
    except Exception as e:
        print(f"Erreur de traitement : {e}")
        reponse = {
            "equipe": "Erreur lors du traitement de la requête"
        }
        return reponse


def traiter_et_categoriser_email(expediteur, sujet, corps):
    """Traite un email et détermine sa catégorie et l'équipe concernée"""
    print("Traitement de l'email en cours...")
    contenu_email = f"Expéditeur: {expediteur}\nSujet: {sujet}\nCorps: {corps}"
    return obtenir_reponse(contenu_email)


def stocker_et_categoriser_email(id_email, expediteur, sujet, corps):
    """Catégorise et stocke un email dans la base de données"""
    reponse = traiter_et_categoriser_email(expediteur, sujet, corps)
    id_equipe = reponse.get("equipe")

    # Stockage dans la base de données
    stocker_email(id_email, expediteur, sujet, corps, id_equipe)

    return id_equipe


def tester_sortie():
    """Fonction de test du système"""
    contenu_test = '''
    Je vous écris pour signaler un problème spécifique que je rencontre avec la plateforme de banque en ligne.

Le problème concerne des incohérences dans l'historique des transactions affiché. Certaines transactions apparaissent en double ou sont manquantes.

Par exemple, le 2 avril, une transaction de 5000€ apparaît deux fois dans mon historique. De plus, des transactions du 4 avril n'apparaissent pas malgré leur confirmation par la banque.

Ces anomalies perturbent ma gestion financière et soulèvent des inquiétudes sur la fiabilité du système.

Je demande à votre équipe technique d'enquêter sur ce problème et de le résoudre rapidement. Il est crucial que la plateforme fournisse des informations exactes pour maintenir la confiance des clients.

Je serais reconnaissant de recevoir des mises à jour régulières sur la résolution de ce problème.'''

    print("Résultat du modèle : ")
    print(obtenir_reponse(contenu_test))


# Point d'entrée pour les tests
if __name__ == "__main__":
    tester_sortie()