from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

def load_rdf(file_path):
    g = Graph()
    g.parse(file_path, format="ttl")
    return g

def query_rdf(g, query):
    prepared_query = prepareQuery(query)
    results = g.query(prepared_query)
    columns = results.vars
    results_list = []
    for row in results:
        result_dict = {}
        for column in columns:
            result_dict[str(column)] = str(row[column])
        results_list.append(result_dict)
    return results_list
