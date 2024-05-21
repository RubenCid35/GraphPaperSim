# Rationale for GraphPaperSim
This document provides a rationale for the validation process used to ensure the accuracy and reliability of the answers provided in the repository documentation.

# Grobid
This code (`grobid.py`) aims to automate the process of extracting key information from research papers, facilitating the other task carried out in this proyect. It leverages an external tool (Grobid) for PDF processing.

# Similarity
This code (`similarity.py`) automates the process of finding similar research papers based on their semantic content extracted from the abstracts. By leveraging all-MiniLM-L6-v2 a pre-trained sentence transformers, it converts text into numerical representations suitable for similarity calculations. The output provides can be used to find potentially related papers within a collection.

# Acknowledgements
Our aim was to extract the targets and persons in the acknowledgements section (`acknowledgment.py`), for this we used bert-base-NER, comparing its result (`acknowledgment.json`) with a manual extraction (`acknowledgment_precision.json`) we have obtained the following results:

| Metric | PER | ORG |
|---|---|---|
| Precision | 0.95 | 0.88 |
| Recall | 0.50 | 0.50 |
| Accuracy | 0.49 | 0.47 |
| F1-Score | 0.66 | 0.64 |

# OpenAlex_OpenAire
This code (`openalex_openaire.py`) automates the process of enriching a dataset of research papers by leveraging external APIs to gather additional details. It then cleans, organizes, and stores this enriched information in a structured format for further uses.

# App
The code code of app.py uses the results of the previous sections have been grouped in the output.ttl file, the application makes use of this document to provide an interface where SPARQL queries can be made to obtain information about the 30 pdfs used as reference. 



