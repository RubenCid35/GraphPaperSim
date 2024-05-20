import dash
import ssl
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

from pyparsing.exceptions import ParseBaseException

# Funciones para cargar y consultar RDF
def load_rdf(file_path):
    g = Graph()
    g.parse(file_path, format="ttl")
    return g

def query_rdf(g, query):
    try: 
        prepared_query = prepareQuery(query)
        results = g.query(prepared_query)
        return [dict(zip(row.labels, row)) for row in results]
    except ParseBaseException as err:
        return err.explain()
    
# Cargar el RDF
g = load_rdf("output.ttl")

# Crear la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Estilos CSS
styles = {
    'textAlign': 'center',
    'margin': 'auto',
    'width': '80%',  # Ancho del contenido principal
    'backgroundColor': '#f4f4f4',  # Color de fondo
    'color': '#333',  # Color del texto
    'fontFamily': 'Arial, sans-serif',  # Fuente del texto
}

# Definir el layout de la aplicación
app.layout = dbc.Container([
    html.H1("Consulta SPARQL", style={'textAlign': 'center', 'color': '#000000'}),
    dbc.Tabs([
        dbc.Tab(label="Consulta Query", tab_id="query"),
        dbc.Tab(label="Sobre Nosotros", tab_id="about"),
    ], id="tabs", active_tab="query"),
    html.Div(id="tab-content", className="p-4")
])

# Callback para cambiar el contenido de las pestañas
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "query":
        return html.Div([
            dcc.Textarea(
                id='sparql-query',
                placeholder='Introduce tu consulta SPARQL aquí',
                style={'width': '100%', 'height': '200px'}
            ),
            html.Button('Enviar consulta', id='submit-button', n_clicks=0, style={'marginTop': '10px'}),
            html.Div(id='results-table-container', style={'marginTop': '20px', 'overflowX': 'auto'})
        ], style=styles)
    elif active_tab == "about":
        return html.Div([
            html.H2("Sobre Nosotros", style={'marginTop': '20px'}),
            html.P("Esta aplicación permite ejecutar consultas SPARQL sobre el conjunto de datos RDF de 30 artículos."),
            html.H3("Desarrollado por:", style={'marginTop': '20px'}),
            html.P("Rubén Cid Costa", style={'margin': '5px 0'}),
            html.P("Rodrigo Durán Andrés", style={'margin': '5px 0'}),
            html.P("Yimin Zhou", style={'margin': '5px 0'}),
        ], style=styles)
    return html.Div("Seleccione una pestaña.")

# Callback para enviar y ejecutar la consulta SPARQL
@app.callback(
    Output('results-table-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('sparql-query', 'value')]
)
def update_table(n_clicks, sparql_query):
    if n_clicks > 0 and sparql_query:
        data = query_rdf(g, sparql_query)
        
        if isinstance(data, str):
            return html.Span(data, style={'color': '#ef4444', 'font-size': '18px', 'width': '100%'})

        if not data:
            return html.Div("No hay resultados.")
        
        # Convertir los resultados a un DataFrame
        df = pd.DataFrame(data)
        
        # Crear la tabla
        return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, style={'width': '100%'})
    return html.Div()

# Ejecutar la aplicación
if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    app.run_server(debug=False, host='0.0.0.0', port=8050)
