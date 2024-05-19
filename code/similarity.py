import torch
import numpy as np
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

from numpy.typing import NDArray
from collections import namedtuple
from typing import List

import json
import warnings

warnings.simplefilter('ignore', category=FutureWarning)

DEBUG: bool = True
SimilarResult = namedtuple('SimilarResult', ['fr', 'to', 'score'])

def get_abstracts( path: str = ""):
    """Reads the file with the abstracs

    Args:
        path (str, optional): Path to the list of objects with the abstracts. Defaults to "results/results.json".

    Returns:
        []: 
    """
    path = 'results/results.json' if len(path) == 0 else path
    with open(path, 'r') as file: 
        abstracts = json.load(file)

    return abstracts

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def get_embeddings(encoder, model, papers):
    """Transforms the given papers abstracts to embeddings using the model

    Args:
        model Pipeline: Pipeline Instance
        papers List[dict[str, str]]: List of papers with the key `abstract`

    Returns: 
        List[NDArray[float]]: list of text embeddings
    """
    vectors = []
    for paper in papers:
        abstract = paper['abstract']

        encoded  = encoder( abstract, padding = True, truncation = True, return_tensors = 'pt' )
        with torch.no_grad():
            model_output = model(**encoded)
        embedding = mean_pooling(model_output, encoded['attention_mask'])
        embedding = F.normalize(embedding, p = 2, dim = 1)
        vectors.append(embedding.numpy())

    return vectors

def cosine_distance(a, b):
    num = np.sum(a * b)
    dem = np.sum(a ** 2) * np.sum(b ** 2)
    return num / np.sqrt(dem)

def get_similar_papers(emb: List[NDArray], thress = 0.7) -> List[SimilarResult]:
    """Estimation of the most similar papers 

    Args:
        emb (List[NDArray]): Lista de 
        thress (float, optional): _description_. Defaults to 0.7.

    Returns:
        List[SimilarResult]: _description_
    """
    similar_matrix = np.zeros((len(emb), len(emb)))
    for i, paper in enumerate(emb[:-1]):
        for j, other in enumerate(emb[i+1:], start = i+1):
            dis = cosine_distance(paper, other)
            similar_matrix[i][j] = dis
            similar_matrix[j][i] = dis

    np.fill_diagonal(similar_matrix, 0) # disable the matrix diagonal. so there are no circular connections in the results
    similar = np.argwhere(similar_matrix >= thress)
    
    results = []
    for pair in similar:
        results.append(SimilarResult(pair[0], pair[1], similar_matrix[pair[0], pair[1]]))

    return results

def main():
    # Load data
    abstracts = get_abstracts()

    # Embedding Model
    model_id = "sentence-transformers/all-MiniLM-L6-v2"
    encoder  = AutoTokenizer.from_pretrained(model_id)
    model    = AutoModel.from_pretrained(model_id)

    embeddings = get_embeddings(encoder, model, abstracts)

    # Get similarity
    thress = .0001
    similar_papers = get_similar_papers(embeddings, thress = thress)    

    # result
    results = []
    for pair in similar_papers:
        result = { "from": abstracts[pair.fr]['id'], "to": abstracts[pair.to]['id'], "similarity": pair.score }
        results.append(result)
        
        if DEBUG:
            print("-" * 60)
            print(f"paper 1 (id: {pair.fr:>3d}):", abstracts[pair.fr]['title'])
            print(f"paper 2 (id: {pair.to:>3d}):", abstracts[pair.to]['title'])
            print(f"score            : {pair.score:6.4f}")
            print("-" * 60)
            print()

    # save results
    with open('results/similarity_results.json', 'w') as end_file:
        json.dump(results, end_file, indent=2)


if __name__ == '__main__': main()