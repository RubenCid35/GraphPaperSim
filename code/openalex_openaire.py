import requests
import json
import re

from tqdm import tqdm


def load_results(file_path):
    """
    Load paper results from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        list: List of paper results.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def clean_text(text):
    # Eliminar caracteres especiales excepto el espacio
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Reemplazar espacios por guiones bajos
    cleaned_text = cleaned_text.replace(' ', '_')
    return cleaned_text


def openalex_result(title):
    """
    Search for papers using OpenAlex API based on the title.

    INPUT:
    - title (str): The title of the paper to search for.

    OUTPUT:
    - dict: Dictionary containing search results.
    """

    # Request URL
    url = f"https://api.openalex.org/works?filter=title.search:{title}"

    # GET request 
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results'][0] if response.json()['meta']['count'] > 0 else None
    else:
        return None

def extract_openalex_info(paper, paper_id):
    """
    Extracts relevant information from the first search result.

    INPUT:
    - paper (dict): Dictionary containing paper information.
    - paper_id (int): Paper ID from results.json

    OUTPUT:
    - dict: Dictionary containing extracted information for the paper.
    - list: List containing information for each author.
    - list: List containing information for each institution.
    """

    if paper is None:
        return None
    
    authors_info = []
    authors_id = []

    institutions_name_set = set()
    institutions_id_set   = set()

    for authorship in paper['authorships']:
        author_name = authorship['author']['display_name']
        author_id = clean_text(author_name)
        authors_id.append(author_id)

        institutions_name = [inst['display_name'] for inst in authorship['institutions'] if authorship['institutions']]
        institutions_id = [clean_text(inst) for inst in institutions_name if institutions_name]

        # Agregar información de instituciones al conjunto
        for inst in institutions_name:
            institutions_name_set.add(inst)
            institutions_id_set.add(clean_text(inst))

        authors_info.append({'id': author_id, 'name': author_name, 'institutions': institutions_id})

    institutions_info = [{"id": clean_text(inst_name), "name": inst_name} for inst_name in institutions_name_set]
    paper_info = {
        'id': paper_id,
        'doi': paper['doi'],
        'title': paper['title'],
        'language': paper['language'],
        'publication_date': paper['publication_date'],
        'authors': authors_id,
        'institutions': list(institutions_id_set)
    }
    return paper_info, authors_info, institutions_info


def remove_duplicates(info):
    """
    Remove duplicate authors from the list based on their IDs.

    INPUT:
    - info (list): List of dictionaries

    OUTPUT:
    - list: List of unique info without duplicates.
    """
    # Create a set to track unique IDs
    unique_ids = set()
    # Create a new list to store unique info
    unique_info = []

    for author_info in info:
        author_id = author_info['id']
        # If the ID is not in unique_ids, add the info to the list of unique info
        if author_id not in unique_ids:
            unique_info.append(author_info)
            unique_ids.add(author_id)

    return unique_info



def main():
    results_json_file = 'results/results.json'
    papers_info_file = 'results/papers_info.json'
    authors_info_file = 'results/authors_info.json'
    institutions_info_file = 'results/institutions_info.json'

    results = load_results(results_json_file)

    all_papers_info = []
    all_authors_info = []
    all_institutions_info = []

    pbar = tqdm(results)
    for paper in pbar:
        pbar.set_description(f"paper: {paper['title'].capitalize()}")
        openalex_info = openalex_result(paper['title'].replace(',', ''))
        paper_info, authors_info, inst_info = extract_openalex_info(openalex_info, paper['id'])
        all_papers_info.append(paper_info)
        all_authors_info = all_authors_info + authors_info
        all_institutions_info = all_institutions_info + inst_info
    
    # Remove duplicates in authors and institutions
    all_authors_info = remove_duplicates(all_authors_info)
    all_institutions_info = remove_duplicates(all_institutions_info)
    
    # Save papers info
    with open(papers_info_file, 'w', encoding='utf-8') as f:
        json.dump(all_papers_info, f, ensure_ascii=False, indent=4)
    
    # Save authors info
    with open(authors_info_file, 'w', encoding='utf-8') as f:
        json.dump(all_authors_info, f, ensure_ascii=False, indent=4)
    
    # Save institutions info
    with open(institutions_info_file, 'w', encoding='utf-8') as f:
        json.dump(all_institutions_info, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()