# Dictionary to hold SPARQL queries with descriptions
sparql_queries = {
    'query1': {
        'description': 'Research articles by research field',
        'query': """
            SELECT ?research_field (COUNT(DISTINCT ?article) AS ?number_of_articles)
            WHERE {  
                ?repository <http://purl.org/pav/retrievedFrom> ?article .
                ?article <http://www.w3.org/ns/prov-o#specializationOf> ?mesh .
                ?mesh <http://www.w3.org/ns/prov-o#generalizationOf> ?top_mesh .
                ?top_mesh <http://www.w3.org/2000/01/rdf-schema#label> ?research_field        
            }
            GROUP BY ?research_field
            ORDER BY DESC(?number_of_articles)
            LIMIT 10
        """
    },
    'query2': {
        'description': 'Research field (MeSH terms) by the number of GitHub repositories that contain at least one Jupyter notebook.',
        'query': """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX repr: <https://w3id.org/reproduceme/>

            SELECT ?research_field (COUNT(DISTINCT ?repository) as ?repository_count) (COUNT(DISTINCT ?repository_nb) as ?repositories_with_notebooks_count)
            WHERE {
                {
                ?repository <http://purl.org/pav/retrievedFrom> ?article .
                }
                UNION
                {
                ?repository_nb <http://purl.org/pav/retrievedFrom>  ?article ;
                            repr:notebooks_count ?notebooks_count .
                    FILTER(xsd:integer(?notebooks_count) > 0)
                }
                ?article <http://www.w3.org/ns/prov-o#specializationOf> ?mesh .
                ?mesh <http://www.w3.org/ns/prov-o#generalizationOf> ?top_mesh .
                ?top_mesh rdfs:label ?research_field
            }
            GROUP BY ?research_field
            ORDER BY DESC(?repository_count)
            LIMIT 10
        """
    },
    'query3': {
        'description': 'Journals with the highest number of articles that had a valid GitHub repository and at least one Jupyter notebook.',
        'query': """
            SELECT ?journal_name (COUNT(?article) as ?article_count)
            WHERE {
                ?article <https://w3id.org/reproduceme/publishedIn> ?journal .
                ?journal <http://www.w3.org/2000/01/rdf-schema#label> ?journal_name .
            }
            GROUP BY ?journal_name
            ORDER BY DESC(?article_count)
            LIMIT 10
        """
    },
    'query4': {
        'description': 'Journals by the number of GitHub repositories and by the number of GitHub repositories with at least one Jupyter notebook.',
        'query': """
            SELECT ?journal_name (COUNT(?repository) as ?repository_count) (COUNT(?repository_nb) as ?repositories_with_notebooks_count) WHERE
            {
                ?article <https://w3id.org/reproduceme/publishedIn> ?journal .
                ?journal <http://www.w3.org/2000/01/rdf-schema#label> ?journal_name .
                {
                ?repository <http://purl.org/pav/retrievedFrom> ?article .
                }
                UNION
                {
                    ?repository_nb <http://purl.org/pav/retrievedFrom> ?article ;
                                <https://w3id.org/reproduceme/notebooks_count> ?notebooks_count .
                    FILTER(<http://www.w3.org/2001/XMLSchema#integer>(?notebooks_count) > 0)
                }
            }
            GROUP BY ?journal_name
            ORDER BY DESC(?repository_count)
            LIMIT 10
        """
    },
    'query5': {
        'description': 'Journals by number of GitHub repositories with Jupyter notebooks.',
        'query': """
            SELECT ?journal_name (COUNT(?repository_nb) AS ?repositories_with_notebooks_count)
                    ?max_notebooks_count
            WHERE {
            {
                SELECT ?journal (MAX(?notebooks_count) AS ?max_notebooks_count)
                WHERE {
                    ?article <https://w3id.org/reproduceme/publishedIn> ?journal .
                    ?journal <http://www.w3.org/2000/01/rdf-schema#label> ?journal_name .  
                    ?repository_nb <http://purl.org/pav/retrievedFrom> ?article ;
                                    <https://w3id.org/reproduceme/notebooks_count> ?notebooks_count .
                    FILTER(<http://www.w3.org/2001/XMLSchema#integer>(?notebooks_count) > 0)  
                }
                GROUP BY ?journal
            }
            ?article <https://w3id.org/reproduceme/publishedIn> ?journal .
            ?journal <http://www.w3.org/2000/01/rdf-schema#label> ?journal_name .  
            ?repository_nb <http://purl.org/pav/retrievedFrom> ?article ;
                            <https://w3id.org/reproduceme/notebooks_count> ?notebooks_count .
            FILTER(<http://www.w3.org/2001/XMLSchema#integer>(?notebooks_count) > 0)  
            }
            GROUP BY ?journal_name  ?max_notebooks_count
            ORDER BY DESC(?repositories_with_notebooks_count)
            LIMIT 10

        """
    },
    'query6': {
        'description': 'Programming languages of the notebooks.',
        'query': """
            SELECT ?language (COUNT(?notebook) as ?notebook_count)
            WHERE {
                ?notebook a <https://w3id.org/reproduceme/Notebook> ;
                            <https://w3id.org/reproduceme/language> ?language .
            }
            GROUP BY ?language
            ORDER BY DESC(?notebook_count)
            LIMIT 10
        """
    },
    'query7': {
        'description': 'Exceptions occurring in Jupyter notebooks in our corpus.',
        'query': """
            SELECT ?exception (COUNT(?exception) AS ?count)
            WHERE {
                ?execution a <https://w3id.org/reproduceme/CellExecution> ;
                    <https://w3id.org/reproduceme/exception> ?exception .
            }
            GROUP BY ?exception
            ORDER BY DESC(?count)
            LIMIT 10
        """
    },
    'query8': {
        'description': 'Jupyter notebook exceptions by research field, taking as a proxy the highest-level MeSH terms of the article associated with the notebook.',
        'query': """
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?research_field (COUNT(?exception) AS ?exception_count)
            WHERE {  
                ?execution  a <https://w3id.org/reproduceme/CellExecution> ;
                    <https://w3id.org/reproduceme/exception> ?exception ;
                    <http://purl.org/pav/retrievedFrom> ?repository .
                ?repository a <http://usefulinc.com/ns/doap#GitRepository> ;
                            <http://purl.org/pav/retrievedFrom> ?article ;
                            <https://w3id.org/reproduceme/notebooks_count> ?notebooks_count .
                ?article a <http://purl.org/spar/fabio/Article> ; 
                        <http://www.w3.org/ns/prov-o#specializationOf> ?mesh .
                ?mesh <http://www.w3.org/ns/prov-o#generalizationOf> ?top_mesh .
                ?top_mesh <http://www.w3.org/2000/01/rdf-schema#label> ?research_field .    
                FILTER (xsd:integer(?notebooks_count)>0)
            }
            GROUP BY ?research_field
            ORDER BY DESC(?exception_count)
            LIMIT 10
        """
    },
    'query9': {
        'description': 'Notebooks with successful executions with same and different results',
        'query': """
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT (COUNT(?processed_different_result) AS ?count_different_result) (COUNT(?processed_same_result) AS ?count_same_result) (?count_same_result + ?count_different_result AS ?count_successful_executions)
            WHERE {
                ?execution a <https://w3id.org/reproduceme/CellExecution> .
                OPTIONAL { ?execution <https://w3id.org/reproduceme/exception> ?exception . }
                OPTIONAL {
                    ?execution <https://w3id.org/reproduceme/processed> ?processed_different_result .
                    FILTER ((xsd:integer(?processed_different_result) = 35) && !bound(?exception))
            }
            OPTIONAL {
                ?execution <https://w3id.org/reproduceme/processed> ?processed_same_result .
                FILTER ((xsd:integer(?processed_same_result) = 51) && !bound(?exception))
            }            
            
            }
        """
    },
    'query10': {
        'description': "Notebooks by search term: 'immun' AND ('stem' OR 'differentiation')",
        'query': """
            SELECT DISTINCT ?notebook_url ?article_label ?keywords WHERE { 
                ?article <https://w3id.org/reproduceme/keywords> ?keywords .
                ?article <http://www.w3.org/2000/01/rdf-schema#label> ?article_label . 
                ?article <https://w3id.org/reproduceme/publishedIn> ?journal .
                ?journal <http://www.w3.org/2000/01/rdf-schema#label> ?journal_label . 
                FILTER (REGEX(LCASE(CONCAT(?keywords, " ", ?article_label, " ", ?journal_label)), "immun"))
                FILTER (REGEX(LCASE(CONCAT(?keywords, " ", ?article_label, " ", ?journal_label)), "\\b(stem|differentiation)"))
                ?article ^<http://purl.org/pav/retrievedFrom> ?repository .
                ?notebook <http://purl.org/pav/retrievedFrom> ?repository .
                ?notebook <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://w3id.org/reproduceme/Notebook> .
                ?notebook <http://www.w3.org/2000/01/rdf-schema#label> ?notebook_label . # filename
                ?repository <https://w3id.org/reproduceme/url> ?repo_url_base . # find repo on GitHub
                BIND(URI(CONCAT( ?repo_url_base, "/blob/master/", ?notebook_label)) AS ?notebook_url) # create clickable link to notebook on GitHub
                FILTER (?notebook_url != "")
            }
        """
    },
    'query11': {
        'description': "Article by keywords, e.g., `open source'",
        'query': """
            SELECT DISTINCT ?article ?keywords WHERE { 
                ?article <https://w3id.org/reproduceme/keywords> ?keywords .
                FILTER (REGEX(LCASE(?keywords), "open(.)source"))
            }
        """
    },
    'query12': {
        'description': "Most common errors in immunology",
        'query': """
            SELECT DISTINCT ?exception (COUNT(?exception) AS ?count) WHERE { 
                ?execution  a <https://w3id.org/reproduceme/CellExecution> ;
                <https://w3id.org/reproduceme/exception> ?exception ;
                <http://purl.org/pav/retrievedFrom> ?repository .
                ?repository a <http://usefulinc.com/ns/doap#GitRepository> ;
                        <http://purl.org/pav/retrievedFrom> ?article .
                ?article  <https://w3id.org/reproduceme/keywords> ?keywords .
                FILTER (REGEX(LCASE(?keywords), "immun"))
            }
            GROUP BY ?exception
            ORDER BY DESC(?count)
        """
    },
    'query13': {
        'description': "Most common errors in Nature journal",
        'query': """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT  ?exception (COUNT(?exception) AS ?count) WHERE { 
                ?execution  a <https://w3id.org/reproduceme/CellExecution> ;
                <https://w3id.org/reproduceme/exception> ?exception ;
                <http://purl.org/pav/retrievedFrom> ?repository .
                ?repository a <http://usefulinc.com/ns/doap#GitRepository> ;
                        <http://purl.org/pav/retrievedFrom> ?article .
                ?article  <https://w3id.org/reproduceme/publishedIn> ?journal .
                ?journal rdfs:label ?journal_name
                FILTER (?journal_name="Nature")
            }
            GROUP BY ?exception
            ORDER BY DESC(?count)
        """
    },
    'query14': {
        'description': "MeSH terms ranked by 'ModuleNotFoundError' frequency",
        'query': """
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?research_field (COUNT(?exception) AS ?exception_count)
            WHERE {  
            ?execution  a <https://w3id.org/reproduceme/CellExecution> ;
                <https://w3id.org/reproduceme/exception> ?exception ;
                <http://purl.org/pav/retrievedFrom> ?repository .
                ?repository a <http://usefulinc.com/ns/doap#GitRepository> ;
                            <http://purl.org/pav/retrievedFrom> ?article ;
                            <https://w3id.org/reproduceme/notebooks_count> ?notebooks_count .
                ?article a <http://purl.org/spar/fabio/Article> ; 
                        <http://www.w3.org/ns/prov-o#specializationOf> ?mesh .
                ?mesh <http://www.w3.org/ns/prov-o#generalizationOf> ?top_mesh .
                ?top_mesh <http://www.w3.org/2000/01/rdf-schema#label> ?research_field .    
                FILTER (?exception='ModuleNotFoundError')
            }
            GROUP BY ?research_field
            ORDER BY DESC(?exception_count)
        """
    },
    'query15': {
        'description': "Repositories by their stargazers count",
        'query': """
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?repo ?stargazers_count WHERE {
                ?repo <https://w3id.org/reproduceme/stargazers_count> ?count. 
                BIND(xsd:float(?count) AS ?stargazers_count)
                FILTER ((?stargazers_count) > 0)
            } 
            ORDER BY DESC(?stargazers_count)
        """
    },
    'query16': {
        'description': "Match articles between FAIR Jupyter and Wikidata via DOI",
        'query': """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            PREFIX wikidata_wd: <http://www.wikidata.org/entity/>
            PREFIX wikidata_wdt: <http://www.wikidata.org/prop/direct/>

            SELECT DISTINCT

            ?fj_article
            ?wikidata
            ?wikidata_label
            ?DOI

            WHERE {
                ?fj_article <https://w3id.org/reproduceme/doi> ?doi .
                BIND(UCASE(?doi) AS ?DOI)
                service <https://query.wikidata.org/sparql> {
                    ?wikidata wikidata_wdt:P356 ?DOI .
                    ?wikidata rdfs:label ?wikidata_label .
                    FILTER (LANG(?wikidata_label) = "en")
            }
            }
            LIMIT 10
        """
    },
    'query17': {
        'description': "Match articles between FAIR Jupyter and Wikidata via PMC ID",
        'query': """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            PREFIX wikidata_wd: <http://www.wikidata.org/entity/>
            PREFIX wikidata_wdt: <http://www.wikidata.org/prop/direct/>

            SELECT DISTINCT

            ?fj_article
            ?wikidata
            ?wikidata_label
            ?pmc

            WHERE {
            ?fj_article <https://w3id.org/reproduceme/pmc> ?pmc .
            service <https://query.wikidata.org/sparql> {
                ?wikidata wikidata_wdt:P932 ?pmc .
                ?wikidata rdfs:label ?wikidata_label .
                FILTER (LANG(?wikidata_label) = "en")
            }
            }
            LIMIT 10
        """
    },
    'query18': {
        'description': "Match articles between FAIR Jupyter and Wikidata via MeSH in different language, i.e Malayalam",
        'query': """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            PREFIX wikidata_wd: <http://www.wikidata.org/entity/>
            PREFIX wikidata_wdt: <http://www.wikidata.org/prop/direct/>

            SELECT DISTINCT

            ?fj_article
            ?wikidata
            ?wikidata_label
            ?DOI

            WHERE {
            ?fj_article <http://www.w3.org/ns/prov-o#specializationOf> ?mesh_url .
            BIND(REPLACE(STR(?mesh_url), ".*MESH/D", "D") AS ?MESH) 
            service <https://query.wikidata.org/sparql> {
                ?wikidata wikidata_wdt:P486 ?MESH .
                ?wikidata rdfs:label ?wikidata_label .
                FILTER (LANG(?wikidata_label) = "ml")
            }
            }
            LIMIT 10
        """
    },
    'query19': {
        'description': "Match articles between FAIR Jupyter and MaRDI via DOI and get co-used software",
        'query': """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX mardi_wd: <https://portal.mardi4nfdi.de/entity/>
            PREFIX mardi_wdt: <https://portal.mardi4nfdi.de/prop/direct/>

            PREFIX bd: <http://www.bigdata.com/rdf#>
            PREFIX wikibase: <http://wikiba.se/ontology#>

            SELECT DISTINCT ?title ?doi ?method ?methodLabel

            WHERE {
            ?fj_article <https://w3id.org/reproduceme/doi> ?doi .

            service <http://query.portal.mardi4nfdi.de/proxy/wdqs/bigdata/namespace/wdq/sparql> {
                ?mardi_paper mardi_wdt:P27 ?doi .
                ?mardi_paper mardi_wdt:P159 ?title .
                
                ?mardi_paper mardi_wdt:P1463 ?method .
                ?method rdfs:label ?methodLabel .
            }

            }
            LIMIT 1000
        """
    },
    'query20': {
        'description': "GitHub repositories and their Software Heritage snapshot",
        'query': """
            # List of GitHub repositories covered by https://doi.org/10.1093/gigascience/giad113 , 
            # with pointers to their Software Heritage snapshots as per https://doi.org/10.5281/zenodo.12806151

            SELECT DISTINCT 
            (URI(?repo_url_base) AS ?GitHub_URL)
            (URI (CONCAT("https://archive.softwareheritage.org/browse/origin/directory/?origin_url=", ENCODE_FOR_URI(STR(?repo_url_base)))) AS ?SWH_URL)
            WHERE {
            ?repository <https://w3id.org/reproduceme/url> ?repo_url_base .
            }
            ORDER BY ASC(?repo_url_base)
        """
    },
    'query21': {
        'description': "Articles and repositories with notebooks in Julia",
        'query': """
            SELECT DISTINCT ?title
            (URI(CONCAT("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC", STR(?pmcid))) AS ?PMC_URL)
            (URI(?repo_url_base) AS ?GitHub_URL)
            ?Notebook_URL
            WHERE {
            ?notebook a <https://w3id.org/reproduceme/Notebook> ;
                        <https://w3id.org/reproduceme/language> "julia" .
            ?notebook <http://purl.org/pav/retrievedFrom> ?repository .
            ?article ^<http://purl.org/pav/retrievedFrom> ?repository .
            ?article <https://w3id.org/reproduceme/pmc> ?pmcid .
            ?article <http://www.w3.org/2000/01/rdf-schema#label> ?title .
            ?notebook <http://www.w3.org/2000/01/rdf-schema#label> ?notebook_label . 
            ?repository <https://w3id.org/reproduceme/url> ?repo_url_base . 
            BIND(URI(CONCAT( ?repo_url_base, "/blob/master/", ?notebook_label)) AS ?Notebook_URL) 
            }
            ORDER BY DESC(?Notebook_URL)
        """
    },
}

# Function to get the queries
def get_sparql_queries():
    return sparql_queries