import os
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import CoherenceModel
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
import json
import multiprocessing
import numpy as np
import random

# Descargar las stopwords y el lematizador de NLTK
import nltk
nltk.download('stopwords')
nltk.download('wordnet')

def load_abstracts(json_file):
    """
    Load abstracts from a JSON file.

    INPUT:
    - json_file (str): Path to the JSON file containing abstracts.

    OUTPUT:
    - abstracts (list): List of abstracts loaded from the JSON file.
    """
    abstracts = []
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            abstracts.append(item["abstract"])
    return abstracts


def preprocess_text(text):
    """
    Preprocess a text.

    INPUT:
    - text (str): Text to be preprocessed.

    OUTPUT:
    - tokens (list): List of preprocessed tokens.
    """

    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(text.lower()) # Tokenización y minúsculas
    tokens = [token for token in tokens if token.isalpha()] # Eliminar puntuación
    tokens = [token for token in tokens if token not in stop_words] # Eliminar stopwords
    tokens = [lemmatizer.lemmatize(token) for token in tokens] # Lematización
    return tokens


def get_optimal_num_topics(corpus, dictionary, preprocessed_abstracts):
    """
    Find the optimal number of topics.

    INPUT:
    - corpus (list): List of document-term frequency vectors.
    - dictionary (gensim.corpora.Dictionary): Dictionary of terms.
    - preprocessed_abstracts (list): List of preprocessed abstracts.

    OUTPUT:
    - optimal_num_topics (int): Optimal number of topics.
    """

    start = 2
    limit = 10
    step = 1
    coherence_values = []

    for num_topics in range(start, limit, step):
        lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=10)
        coherence_model = CoherenceModel(model=lda_model, texts=preprocessed_abstracts, dictionary=dictionary, coherence='c_v')
        coherence_value = coherence_model.get_coherence()
        coherence_values.append((num_topics, coherence_value))

    optimal_num_topics = max(coherence_values, key=lambda x: x[1])[0]
    print("coherence:", coherence_values)
    print()
    print(f"Optimal number of topics: {optimal_num_topics}")
    return optimal_num_topics


def train_lda_model(corpus, dictionary, num_topics):
    """
    Train the LDA model.

    INPUT:
    - corpus (list): List of document-term frequency vectors.
    - dictionary (gensim.corpora.Dictionary): Dictionary of terms.
    - num_topics (int): Number of topics.

    OUTPUT:
    - lda_model (gensim.models.LdaModel): Trained LDA model.
    """

    lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=10, random_state=98)
    return lda_model


def get_document_topics(lda_model, corpus):
    """
    Get topic distributions for each document.

    INPUT:
    - lda_model (gensim.models.LdaModel): Trained LDA model.
    - corpus (list): List of document-term frequency vectors.

    OUTPUT:
    - document_topics (list): List of dictionaries containing document IDs and their corresponding topic distributions.
    """
    
    document_topics = []
    for i, doc in enumerate(corpus):
        topic_distribution = lda_model.get_document_topics(doc)
        document_topics.append({"id": i, "topic_distribution": [(topic, prob) for topic, prob in topic_distribution]})
    return document_topics


def main():
    # Define the location of the JSON file containing the abstracts
    abstracts_json_file = 'results/results.json'
    topics_json_file = 'results/topics.json'
    topics_prob_json_file = 'results/topics_prob.json'

    # Load abstracts
    abstracts = load_abstracts(abstracts_json_file)

    # Preprocess abstracts
    preprocessed_abstracts = [preprocess_text(abstract) for abstract in abstracts]

    # Create a dictionary of terms
    dictionary = corpora.Dictionary(preprocessed_abstracts)

    # Filter out infrequent and uninformative terms
    dictionary.filter_extremes(no_below=5, no_above=0.5)

    # Represent documents using the Bag of Words matrix
    corpus = [dictionary.doc2bow(abstract) for abstract in preprocessed_abstracts]

    # Get the optimal number of topics
    optimal_num_topics = get_optimal_num_topics(corpus, dictionary, preprocessed_abstracts)

    # Train the LDA model with the optimal number of topics
    lda_model = train_lda_model(corpus, dictionary, optimal_num_topics)

    # Explore the results
    topics_list = [{"id": i, "words": ", ".join([word for word, _ in lda_model.show_topic(i)])} for i in range(optimal_num_topics)]
    
    # Save the topics to a JSON file
    with open(topics_json_file, 'w', encoding='utf-8') as f:
        json.dump(topics_list, f, ensure_ascii=False, indent=4)

    print("Topics saved to 'topics.json'")

    # Get topic distributions for each document
    document_topics = get_document_topics(lda_model, corpus)
    print(document_topics)
    topics_prob = []
    for doc in document_topics:
        max_topic, max_prob = max(doc["topic_distribution"], key=lambda x: x[1])
        topics_prob.append({"id": doc["id"], "topic_id": max_topic, "topic_prob": float(max_prob)})

    # # Save topic probabilities to a separate JSON file
    with open(topics_prob_json_file, 'w', encoding='utf-8') as f:
        json.dump(topics_prob, f, ensure_ascii=False, indent=4)

    print("Topics and probabilities added to 'results/topics_prob.json'")


if __name__ == "__main__":
    multiprocessing.freeze_support()  # descomentar si se ejecuta en windows
    main()