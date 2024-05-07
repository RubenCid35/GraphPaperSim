import requests
from bs4 import BeautifulSoup
import os
import json


def grobid_xml(pdf_path):
    """
    Extracts XML content from a PDF file using the Grobid API.
    INPUT:
    - pdf_path (str): Path to the PDF file to be processed.

    OUTPUT:
    - BeautifulSoup object representing the XML response from Grobid if successful,
      None otherwise.
    """
    
    grobid_url = 'http://localhost:8070/api/processFulltextDocument'
    with open(pdf_path, 'rb') as file:
        # Create the request to send to the Grobid API
        params = {'input': (pdf_path, file, 'application/pdf')}
        # Send the request to the Grobid API
        response = requests.post(grobid_url, files=params)
        if response.status_code == 200:
            # Parse the XML response from Grobid
            soup = BeautifulSoup(response.text, 'xml')
        else:
            print(f"Error: Failed to retrieve content from {pdf_path}. Status code: {response.status_code}") 
            return None
    return soup


def extract_abstract(xml):
    """
    Extracts the abstract from an XML document obtained from Grobid processing.

    INPUT:
    - xml (BeautifulSoup): BeautifulSoup object representing the XML document.

    OUTPUT:
    - Abstract text extracted from the XML document.
    """

    # Verify that grobid_results is not empty
    if not xml:
        return None
    else:
        abstract = xml.find('abstract')
        if abstract:
            return abstract.text.strip()
        else:
            return None

def extract_title(xml):
    """
    Extracts the title from an XML document obtained from Grobid processing.

    INPUT:
    - xml (BeautifulSoup): BeautifulSoup object representing the XML document.

    OUTPUT:
    - Title extracted from the XML document.
    """

    # Verify that grobid_results is not empty
    if not xml:
        return None
    else:
        title = xml.find('titleStmt').find('title', type='main')
        if title:
            return title.text.strip()
        else:
            return None

def extract_ack(xml):
    """
    Extracts acknowledgement from an XML document obtained from Grobid processing.

    INPUT:
    - xml (BeautifulSoup): BeautifulSoup object representing the XML document.

    OUTPUT:
    - Acknowledgement extracted from the XML document.
    """

    # Verify that grobid_results is not empty
    if not xml:
        return None
    else:
        ack = xml.find('div', type='acknowledgement')
        if ack:
            return ack.find('p').text.strip()
        else:
            return None


articles_folder = 'papers'
# Check if the 'results' directory exists, if not, create it
results_dir = "./results"
if not os.path.exists(results_dir):
    os.makedirs(results_dir)
    print("Directory 'results' created successfully.")


results = []
id_counter = 0

for filename in os.listdir(articles_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(articles_folder, filename)
        print(f"Processing: {pdf_path}")
        
        # XML
        xml = grobid_xml(pdf_path)
        
        if xml:
            # Extract title, abstract, ack
            title = extract_title(xml)
            abstract = extract_abstract(xml)
            acknowledgment = extract_ack(xml)
            
            results.append({
                "id": id_counter,
                "title": title,
                "abstract": abstract,
                "acknowledgment": acknowledgment
            })
            
            id_counter += 1
            print(f"Results saved for {filename}")
        else:
            print(f"Error processing {pdf_path}")

output_file = os.path.join("results", "results.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Processing complete.")

## docker run -t --rm -p 8070:8070 lfoppiano/grobid:0.7.2 