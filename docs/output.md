## Running examples
In the application, there are two tabs: "Consulta-Query" (for querying the Knowledge Graph) and "Sobre Nosotros".

Below is an example of a query.

```
PREFIX onto: <http://upm.ontology.es/papers#>
SELECT ?sub ?obj WHERE {
  ?sub onto:hasName ?obj .
} LIMIT 10
```
