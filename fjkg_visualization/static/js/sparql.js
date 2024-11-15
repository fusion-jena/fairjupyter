document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    const resultsPerPage = 10;

    const entityItemsContainer = document.getElementById('entityItems');
    const entityAttributesContainer = document.getElementById('entityAttributes');
    const entityAttributesMainContainer = document.getElementById('entityAttributesContainer');
    const resultsDiv = document.getElementById('resultsContainer');
    const prevEntityPageButton = document.getElementById('prevEntityPage');
    const nextEntityPageButton = document.getElementById('nextEntityPage');
    const loadingSpinner = document.getElementById('loadingSpinner');    
    const graphContainer = document.getElementById('graphContainer'); 
    const networkContainer = document.getElementById('network'); // For graph visualization

    const selectMessage = document.getElementById('selectMessage');
    let selectedEntity = null; // To track the currently selected entity

    // Show the loading spinner
    function showLoading() {
        loadingSpinner.style.display = 'block';
    }

    // Hide the loading spinner
    function hideLoading() {
        loadingSpinner.style.display = 'none';
    }

    // Show the results container and select message when data is available
    function showResultsContainer() {
        resultsDiv.classList.remove("hidden");
        selectMessage.classList.remove("hidden");
    }

    // Hide the results container when no data is available
    function hideResultsContainer() {
        resultsDiv.classList.add("hidden");
        selectMessage.classList.add("hidden"); // Hide the "Select an entry" message
    }

    // Show the graph container when visualizing the graph
    function showGraphContainer() {
        graphContainer.classList.remove("hidden");
    }
    
    // Show the graph container when visualizing the graph
    function showEntityAttributesMainContainer() {
        entityAttributesMainContainer.classList.remove("hidden");
    }

    // Fetch and display entity items
    function loadEntityItems(entityType, page) {
        // entityItemsContainer.innerHTML = ''; // Clear previous items
        // entityAttributesContainer.innerHTML = ''; // Clear attributes section

        entityItemsContainer.innerHTML = ''; // Clear previous items
        entityAttributesContainer.innerHTML = ''; // Clear attributes section
        selectedEntity = null; // Reset selected entity
        showLoading();
        fetch(`/fj/entity-items?type=${entityType}&page=${page}&resultsPerPage=${resultsPerPage}`)
            .then(response => response.json())
            .then(data => {    
                

                if (data.items.length > 0) {
                    showResultsContainer(); // Show the results container and message
                } else {
                    hideResultsContainer(); // Hide the container if no results are found
                }

                // Populate entity items
                data.items.forEach(item => {
                    const entityItem = document.createElement('a');
                    entityItem.href = "#";
                    entityItem.classList.add("list-group-item", "list-group-item-action");
                    entityItem.textContent = item.label || item.uri;
                    entityItem.dataset.uri = item.uri;

                    // Event listener for clicking on an entity item
                    entityItem.addEventListener('click', (event) => {
                        event.preventDefault();
                        highlightSelectedEntity(entityItem); // Highlight the selected entity
                        loadEntityAttributes(item.uri);
                    });

                    entityItemsContainer.appendChild(entityItem);
                });

                // Manage pagination buttons
                prevEntityPageButton.disabled = page === 1;
                nextEntityPageButton.disabled = data.isLastPage;
            })
            .catch(error => {
                console.error('Error fetching entity items:', error);
            })
            .finally(() => hideLoading());
    }

    // Fetch and display the attributes for a specific entity
    function loadEntityAttributes(uri) {
        showLoading();
        fetch(`/fj/entity-attributes?uri=${encodeURIComponent(uri)}`)
            .then(response => response.json())
            .then(data => {
                // Show the results container when results are found
                showResultsContainer();
                showEntityAttributesMainContainer();
                // Show the graph container when results are found
                showGraphContainer();                
                
                entityAttributesContainer.innerHTML = ''; // Clear previous attributes
    
                // Convert the attributes object into an array format { predicate, object }
                const attributesArray = Object.entries(data.attributes).map(([predicate, object]) => ({
                    predicate: predicate,
                    object: object
                }));
    
                // Display attributes in the UI
                attributesArray.forEach(attribute => {
                    const attributeItem = document.createElement('p');
    
                    // Check if the predicate is a URL and handle it accordingly
                    const predicateContent = isUri(attribute.predicate)
                        ? (attribute.predicate.startsWith('https://w3id.org/reproduceme') 
                            ? `<a href="https://w3id.org/reproduceme" target="_blank">${attribute.predicate}</a>` 
                            : `<a href="${attribute.predicate}" target="_blank">${attribute.predicate}</a>`)
                        : attribute.predicate;
    
                    // Check if the object is a URL and handle it accordingly
                    const objectContent = isUri(attribute.object)
                        ? (attribute.object.startsWith('https://w3id.org/reproduceme') 
                            ? `<a href="https://w3id.org/reproduceme" target="_blank">${attribute.object}</a>` 
                            : `<a href="${attribute.object}" target="_blank">${attribute.object}</a>`)
                        : attribute.object;
    
                    // Display the predicate and object, either as links or plain text
                    attributeItem.innerHTML = `<strong>${predicateContent}</strong>: ${objectContent}`;
    
                    entityAttributesContainer.appendChild(attributeItem);
                });
    
                // Visualize the graph for the entity using the array format
                visualizeGraph(uri, attributesArray);
            })
            .catch(error => console.error('Error fetching entity attributes:', error))
            .finally(() => hideLoading());
    }
    

    // Create a graph visualization using vis.js
    function visualizeGraph(entityUri, attributes) {
        const nodes = [];
        const edges = [];

        // Add the main entity as the center node
        nodes.push({
            id: entityUri,
            label: entityUri,
            color: '#ffcc00',
            size: 30,
            font: { size: 20, color: '#000000' }
        });

        // Add the attributes as nodes and edges
        attributes.forEach(attribute => {
            const objectNode = isUri(attribute.object) ? attribute.object : `Literal: ${attribute.object}`;
            const predicateLabel = predicateLabels[attribute.predicate] || attribute.predicate;

            // Add object node if it's a URI
            if (isUri(attribute.object)) {
                nodes.push({
                    id: attribute.object,
                    label: attribute.object,
                    color: '#66ccff',
                    size: 20,
                    font: { size: 14, color: '#000000' }
                });
                // Add edges from entity to the object node
                edges.push({ from: entityUri, to: attribute.object, label: predicateLabel, width: 2 });
            } else {
                // If the object is a literal, link it as a literal node
                edges.push({ from: entityUri, to: objectNode, label: predicateLabel, width: 2 });
            }
        });

        // Initialize network graph
        const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
        const options = {
            nodes: {
                shape: 'dot',
                font: { size: 14, color: '#000000' },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                arrows: { to: true },
                smooth: { type: 'continuous' },
                font: { size: 12, color: '#000000' },
                color: { color: '#848484', highlight: '#ff0000', hover: '#ff0000' },
                width: 2
            },
            layout: { improvedLayout: true },
            interaction: { hover: true, tooltipDelay: 200 }
        };
        const network = new vis.Network(networkContainer, data, options);

        // Show graph container
        showGraphContainer();

        // Handle click events on nodes
        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                const clickedNode = params.nodes[0];
                if (isUri(clickedNode)) {
                    loadEntityAttributes(clickedNode);  // Fetch details for the clicked URI node
                }
            }
        });
    }

    // Function to highlight the selected entity item
    function highlightSelectedEntity(entityItem) {
        // Remove the highlight from the previously selected entity
        if (selectedEntity) {
            selectedEntity.classList.remove('active');
        }

        // Highlight the new entity
        entityItem.classList.add('active');
        selectedEntity = entityItem; // Update the selected entity reference
    }

    // Handle breadcrumb clicks for selecting entity type
    document.querySelectorAll('.breadcrumb-item a').forEach(breadcrumb => {
        breadcrumb.addEventListener('click', function() {
            selectedEntityType = this.dataset.entity;
            currentPage = 1;
            loadEntityItems(selectedEntityType, currentPage);
        });
    });

    // Pagination handlers for entity items
    prevEntityPageButton.addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            loadEntityItems(selectedEntityType, currentPage);
        }
    });

    nextEntityPageButton.addEventListener('click', function() {
        currentPage++;
        loadEntityItems(selectedEntityType, currentPage);
    });

    // Utility functions
    function isUri(str) {
        return str.startsWith("http://") || str.startsWith("https://");
    }

    // Human-readable labels for RDF predicates
    const predicateLabels = {
        "http://www.w3.org/2000/01/rdf-schema#label": "Title",
        "https://w3id.org/reproduceme/iso_abbrev": "ISO Abbreviation",
        "https://w3id.org/reproduceme/issn": "ISSN",
        "https://w3id.org/reproduceme/nlm_ta": "NLM Title Abbreviation",
        "https://w3id.org/reproduceme/publisher_name": "Publisher",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "Type"
    };
});
