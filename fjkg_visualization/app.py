from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from SPARQLWrapper import SPARQLWrapper, JSON
import logging
#from logging.handlers import RotatingFileHandler
from sparql_queries import get_sparql_queries

app = Flask(__name__, static_url_path='/fj/static')
app.config['APPLICATION_ROOT'] = '/fj'

# SPARQL endpoint configuration
sparql_endpoint = SPARQLWrapper("https://reproduceme.uni-jena.de/fairjupyter/sparql")

ENTITY_TYPE_URIS = {
    "Journal": "http://purl.org/spar/fabio/Journal",
    "Article": "http://purl.org/spar/fabio/Article",
    "Repository": "http://usefulinc.com/ns/doap#GitRepository",
    "Notebook": "https://w3id.org/reproduceme/Notebook",
    "Author": "https://w3id.org/reproduceme/Author",
    "MESH": "http://purl.bioontology.org/ontology/MESH/",
    "GitRepositoryRelease": "https://w3id.org/reproduceme/GitRepositoryRelease",
    "NotebookCodeStyle": "https://w3id.org/reproduceme/NotebookCodeStyleError",
    "Cell": "https://w3id.org/reproduceme/Cell",
    "CellExecution": "https://w3id.org/reproduceme/CellExecution",
    "CellFeature": "https://w3id.org/reproduceme/CellFeature",
    "CellModule": "https://w3id.org/reproduceme/CellModule",
    "CellName": "https://w3id.org/reproduceme/CellName",
    "CodeAnalysis": "https://w3id.org/reproduceme/CodeAnalysis",
    "MarkdownFeature": "https://w3id.org/reproduceme/MarkdownFeature",
    "RepositoryFile": "https://w3id.org/reproduceme/File",
    "NotebookFeature": "https://w3id.org/reproduceme/NotebookFeature",
    "NotebookMarkdown": "https://w3id.org/reproduceme/NotebookMarkdown",
    "NotebookModule": "https://w3id.org/reproduceme/NotebookModule",
    "NotebookName": "https://w3id.org/reproduceme/NotebookName",
}

# Get SPARQL queries from the external file
sparql_queries = get_sparql_queries()

# Route to serve the home page
@app.route('/fj/')
def home():
    return render_template('home.html')

# Route for the FAIR Jupyter Knowledge Graph Browser page
@app.route('/fj/browser')
def browser():
    return render_template('browser.html')

# Route for the SPARQL endpoint page
@app.route('/fj/sparql')
def sparql():
    return render_template('sparql.html')

# Route for the SPARQL query page
@app.route('/fj/querylist')
def querylist():
    return render_template('querylist.html', queries=sparql_queries)

# Route for the contact page
@app.route('/fj/contact')
def contact():
    return render_template('contact.html')

# Route to fetch entity details
@app.route("/fj/entity/<path:entity_id>")
def get_entity_details(entity_id):
    print(f"Fetching details for: {entity_id}")

    query = f"""
    SELECT ?predicate ?object WHERE {{
        <{entity_id}> ?predicate ?object.
    }}
    """
    sparql_endpoint.setQuery(query)
    sparql_endpoint.setReturnFormat(JSON)

    try:
        results = sparql_endpoint.query().convert()
        attributes = [{"predicate": str(result["predicate"]["value"]), "object": str(result["object"]["value"])} for result in results["results"]["bindings"]]
        return jsonify({"entity": entity_id, "attributes": attributes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for search functionality
@app.route("/fj/search")
def search_entities():
    query_str = request.args.get('q', '').lower()
    page = int(request.args.get('page', 1))
    results_per_page = int(request.args.get('resultsPerPage', 10))

    print(f"query_str: {query_str}")

    # Construct the SPARQL query to search for subjects and their labels
    query = f"""
    SELECT DISTINCT ?subject ?label WHERE {{
        ?subject ?predicate ?object.
        OPTIONAL {{
            ?subject <http://www.w3.org/2000/01/rdf-schema#label> ?label.
        }}
        FILTER(
            CONTAINS(LCASE(str(?subject)), LCASE("{query_str}")) ||
            (BOUND(?label) && CONTAINS(LCASE(str(?label)), LCASE("{query_str}")))
        )
    }} ORDER BY ?subject LIMIT {results_per_page} OFFSET {(page - 1) * results_per_page}
    """

    print(f"query: {query}")

    # Execute the SPARQL query
    sparql_endpoint.setQuery(query)
    sparql_endpoint.setReturnFormat(JSON)

    try:
        sparql_results = sparql_endpoint.query().convert()
        print(f"sparql_results: {sparql_results}")

        # Extract only the URIs and labels from the results
        entities = []
        for result in sparql_results["results"]["bindings"]:
            subject_uri = str(result["subject"]["value"])
            label = str(result["label"]["value"]) if "label" in result else subject_uri  # Use URI if label is not available
            entities.append({"uri": subject_uri, "label": label})

        # Return the URIs and labels as JSON
        if entities:
            print(f"results: {entities}")
            return jsonify({"results": entities})
        else:
            return jsonify({"error": "No results found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Fetch the first 10 items for the selected entity type
@app.route("/fj/entity-items")
def entity_items():
    entity_type = request.args.get('type')
    print(f"entity_type: {entity_type}")
    page = int(request.args.get('page', 1))
    results_per_page = int(request.args.get('resultsPerPage', 10))

    # Look up the corresponding URI for the selected entity type
    if entity_type in ENTITY_TYPE_URIS:
        entity_uri = ENTITY_TYPE_URIS[entity_type]
    else:
        return jsonify({"error": "Unknown entity type"}), 400

    print(f"entity_uri: {entity_uri}")
    # SPARQL query to fetch the items of the selected entity type
    query = f"""
    SELECT DISTINCT ?subject ?label WHERE {{
        ?subject a <{entity_uri}>.
        OPTIONAL {{
            ?subject <http://www.w3.org/2000/01/rdf-schema#label> ?label.
        }}
    }} LIMIT {results_per_page} OFFSET {(page - 1) * results_per_page}
    """
    print(f"query: {query}")
    sparql_endpoint.setQuery(query)
    sparql_endpoint.setReturnFormat(JSON)

    try:
        sparql_results = sparql_endpoint.query().convert()
        # Prepare response data
        items = [{"uri": str(result["subject"]["value"]), "label": str(result["label"]["value"]) if "label" in result else str(result["subject"]["value"])} for result in sparql_results["results"]["bindings"]]

        # Determine if this is the last page
        count_query = f"SELECT (COUNT(DISTINCT ?subject) AS ?count) WHERE {{ ?subject a <{entity_uri}>. }}"
        sparql_endpoint.setQuery(count_query)
        sparql_endpoint.setReturnFormat(JSON)
        count_results = sparql_endpoint.query().convert()
        total_count = int(count_results["results"]["bindings"][0]["count"]["value"])
        is_last_page = (page * results_per_page) >= total_count

        return jsonify({"items": items, "isLastPage": is_last_page})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Fetch the attributes of a specific entity
@app.route("/fj/entity-attributes")
def entity_attributes():
    entity_uri = request.args.get('uri')
    print(f"entity_uri: {entity_uri}")

    # SPARQL query to fetch all attributes of the selected entity
    query = f"""
    SELECT ?predicate ?object WHERE {{
        <{entity_uri}> ?predicate ?object.
    }}
    """
    print(f"query: {query}")
    sparql_endpoint.setQuery(query)
    sparql_endpoint.setReturnFormat(JSON)

    try:
        sparql_results = sparql_endpoint.query().convert()
        # Prepare response data
        attributes = {str(result["predicate"]["value"]): str(result["object"]["value"]) for result in sparql_results["results"]["bindings"]}

        return jsonify({"attributes": attributes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fj/execute-query', methods=['POST'])
def execute_query():
    query_name = request.json.get('query_name')
    print(f"query_name: {query_name}")

    if query_name not in sparql_queries:
        return jsonify({'error': 'Invalid query name'}), 400

    # Get the SPARQL query
    sparql_query = sparql_queries[query_name]['query']
    print(f"sparql_queries[query_name]: {sparql_query}")

    # Set the query in SPARQLWrapper
    sparql_endpoint.setQuery(sparql_query)
    sparql_endpoint.setReturnFormat(JSON)

    try:
        results = sparql_endpoint.query().convert()
        variables = results['head']['vars']
        bindings = results['results']['bindings']

        # Process results into a list of dictionaries
        data = []
        for binding in bindings:
            row = {var: binding[var]['value'] if var in binding else None for var in variables}
            data.append(row)

        return jsonify({
            'sparql_query': sparql_query,  # Send back the SPARQL query
            'variables': variables,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Set up production logging
# if not app.debug:
#     file_handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
#     file_handler.setLevel(logging.WARNING)
#     app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3031, debug=True)  # Start the Flask app (it will run on port 5000 by default)
