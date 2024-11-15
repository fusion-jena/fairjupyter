let currentPage = 1;
const resultsPerPage = 10;

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

// Show the results, pagination, and entity details when data is available
function showResultsContainer() {
    document.getElementById("resultsContainer").classList.remove("hidden");
}

// Show the graph container when visualizing the graph
function showGraphContainer() {
    document.getElementById("graphContainer").classList.remove("hidden");
}

async function fetchResults(page) {
    const query = document.getElementById("searchInput").value;
    if (!query) return;

    showLoading();
    let searchResults = await fetch(`/fj/search?q=${encodeURIComponent(query)}&page=${page}&resultsPerPage=${resultsPerPage}`)
        .then(response => response.json())
        .catch(err => console.error("Error fetching search results:", err))
        .finally(() => hideLoading());

    let resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";

    // Handle case if no results found
    if (searchResults.error) {
        resultsDiv.innerHTML = `<p>No results found for "${query}"</p>`;
        document.getElementById("prevPage").disabled = true;
        document.getElementById("nextPage").disabled = true;
        return;
    }

    // Show the results container when results are found
    showResultsContainer();

    // Display search results (URIs and labels)
    searchResults.results.forEach(result => {
        let resultItem = document.createElement("p");
        resultItem.innerHTML = `<a href="#" onclick="fetchEntity('/fj/entity/${result.uri}')">${result.label || result.uri}</a>`;
        resultsDiv.appendChild(resultItem);
    });

    // Enable/disable pagination buttons
    document.getElementById("prevPage").disabled = (currentPage <= 1);
    // Disable next button if there are fewer results than the results per page
    document.getElementById("nextPage").disabled = (searchResults.results.length < resultsPerPage);
}

document.getElementById("searchButton").addEventListener("click", () => {
    currentPage = 1; // Reset to the first page on new search
    fetchResults(currentPage);
});

document.getElementById("prevPage").addEventListener("click", () => {
    if (currentPage > 1) {
        currentPage--;
        fetchResults(currentPage);
    }
});

document.getElementById("nextPage").addEventListener("click", () => {
    currentPage++;
    fetchResults(currentPage);
});

// Human-readable labels for common RDF predicates
const predicateLabels = {
    "http://www.w3.org/2000/01/rdf-schema#label": "Title",
    "https://w3id.org/reproduceme/iso_abbrev": "ISO Abbreviation",
    "https://w3id.org/reproduceme/issn": "ISSN",
    "https://w3id.org/reproduceme/nlm_ta": "NLM Title Abbreviation",
    "https://w3id.org/reproduceme/publisher_name": "Publisher",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "Type"
};

// Function to check if a string is a URI
function isUri(str) {
    return str.startsWith("http://") || str.startsWith("https://");
}

// Function to create a graph visualization using vis.js
function visualizeGraph(entityUri, attributes) {
    const nodes = [];
    const edges = [];

    // Add the main entity as the center node
    nodes.push({ id: entityUri, label: entityUri, color: '#ffcc00', size: 30, font: { size: 20, color: '#000000' } });

    // Add the attributes as nodes and edges
    attributes.forEach(attribute => {
        const objectNode = isUri(attribute.object) ? attribute.object : `Literal: ${attribute.object}`;
        const predicateLabel = predicateLabels[attribute.predicate] || attribute.predicate;

        // Add object node if it's a URI
        if (isUri(attribute.object)) {
            nodes.push({ id: attribute.object, label: attribute.object, color: '#66ccff', size: 20, font: { size: 14, color: '#000000' } });
        }

        // Add edges from entity to the object node
        edges.push({ from: entityUri, to: objectNode, label: predicateLabel, width: 2 });
    });

    // Create a network graph
    const container = document.getElementById('network');
    const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };

    const options = {
        nodes: {
            shape: 'dot',
            font: {
                size: 14,
                color: '#000000',
                face: 'arial'
            },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            arrows: { to: true },
            smooth: { type: 'continuous' },
            font: {
                size: 12,
                color: '#000000'
            },
            color: {
                color: '#848484',
                highlight: '#ff0000',
                hover: '#ff0000'
            },
            width: 2
        },
        layout: {
            improvedLayout: true
        },
        interaction: {
            hover: true,
            tooltipDelay: 200
        }
    };

    // Initialize the network
    const network = new vis.Network(container, data, options);

    // Show the graph container when graph data is loaded
    showGraphContainer();

    // Handle click events on nodes to fetch new entity details
    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            const clickedNode = params.nodes[0];
            if (isUri(clickedNode)) {
                fetchEntity(clickedNode);  // Fetch details for the clicked URI node
            }
        }
    });
}

// Function to fetch and display entity details
async function fetchEntity(entityUri) {
    showLoading();
    let entityDetails = await fetch(`/fj/entity/${encodeURIComponent(entityUri)}`)
        .then(response => response.json())
        .catch(err => console.error("Error fetching entity details:", err))
        .finally(() => hideLoading());

    let entityDiv = document.getElementById("entityDetails");
    entityDiv.innerHTML = "";

    // Handle case if entity not found
    if (entityDetails.error) {
        entityDiv.innerHTML = `<p>Entity not found: ${entityUri}</p>`;
        return;
    }

    // Display the entity URI at the top
    entityDiv.innerHTML = `<h3>Entity: ${entityDetails.entity}</h3>`;

    // Create a list for attributes
    let attributesList = document.createElement("ul");

    // Loop through the attributes and display predicate and object
    entityDetails.attributes.forEach(attribute => {
        let listItem = document.createElement("li");

        // Get human-readable label or use the predicate itself if not found
        let predicateLabel = predicateLabels[attribute.predicate] || attribute.predicate;

        // If the object is a URI, make it a clickable link
        if (isUri(attribute.object)) {
            listItem.innerHTML = `<strong>${predicateLabel}</strong>: <a href="#" onclick="fetchEntity('${attribute.object}')">${attribute.object}</a>`;
        } else {
            // Otherwise, just display the object as plain text
            listItem.innerHTML = `<strong>${predicateLabel}</strong>: ${attribute.object}`;
        }

        attributesList.appendChild(listItem);
    });

    // Append the attributes list to the entity details div
    entityDiv.appendChild(attributesList);

    // Visualize the entity and its relationships as a graph
    visualizeGraph(entityDetails.entity, entityDetails.attributes);
}