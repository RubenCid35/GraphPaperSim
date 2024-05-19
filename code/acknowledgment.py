import requests
import json
import re

# Load model directly
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

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

def filtrar_entidades_por_score_y_etiquetas(lista, score_umbral, acknowledgment, indice):
    """
    Filtra las entidades de una lista según el score y las etiquetas especificadas.

    Args:
    - lista (list): Lista de diccionarios, cada uno representando una entidad con las siguientes claves:
                    'entity', 'score', 'index', 'word', 'start', 'end'.
    - score_umbral (float): Umbral para el score. Se mantienen las entidades con score mayor a este valor.
    Returns:
    - dict: Diccionario donde las claves son las etiquetas y los valores son listas de palabras correspondientes a esas etiquetas.
    """
    output = {"ID": indice, "PER" : [], "ORG" : [], "LOC" : [], "MISC" : []}
    
    inicio = 0; final = 0
    while len(lista) > 0:
        if lista[0]["score"] >= score_umbral and lista[0]["entity"].startswith("B-"):
            categoria = lista[0]["entity"][2:]
            inicio = lista[0]["start"]
            final = lista[0]["end"]
            lista.pop(0)
            
            continua = True
            while continua:
                if len(lista) > 0 and (lista[0]["entity"].startswith("I-") or "#" in lista[0]["word"]):
                    final = lista[0]["end"]
                    lista.pop(0)
                else:
                    continua = False
                    
            output[categoria].append(clean_text(acknowledgment[inicio:final]))
        
        else:
            lista.pop(0)
            
    return output

def main():
    results_json_file = 'results/results.json'
    acknowledgment_json_file = 'results/acknowledgment.json'

    results = load_results(results_json_file)
    # print(results)
    
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    
    almacen = []
    
    for paper in results:
        acknowledgment = paper['acknowledgment']
        entidades = filtrar_entidades_por_score_y_etiquetas(nlp(acknowledgment), 0.90, acknowledgment, paper["id"])
        almacen.append(entidades)
        
    # Save papers acknowledgment
    with open(acknowledgment_json_file, 'w', encoding='utf-8') as f:
        json.dump(almacen, f, ensure_ascii=False, indent=4)
        

if __name__ == "__main__":
    main()
