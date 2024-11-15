document.addEventListener('DOMContentLoaded', function () {
    const queryLinks = document.querySelectorAll('.query-link');
    const queryDetails = document.getElementById('queryDetails');
    const sparqlQuery = document.getElementById('sparqlQuery');
    const queryResults = document.getElementById('queryResults');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Show loading spinner
    function showLoading() {
        loadingSpinner.style.display = 'block';
    }

    // Hide loading spinner
    function hideLoading() {
        loadingSpinner.style.display = 'none';
    }

    // Handle clicking on a query link
    queryLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const queryName = this.getAttribute('data-query-name');

            // Show the query details section and clear previous results
            queryResults.innerHTML = '';
            queryDetails.style.display = 'block';
            sparqlQuery.textContent = ''; // Clear previous SPARQL query

            // Show the loading spinner while waiting for results
            showLoading();

            // Fetch query details and results
            fetch('/fj/execute-query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query_name: queryName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }

                // Display the SPARQL query as soon as we receive it
                sparqlQuery.textContent = data.sparql_query;
                

                // Display the results in a table
                const variables = data.variables;
                const rows = data.data;

                let table = '<table class="table table-bordered">';
                table += '<thead><tr>';
                variables.forEach(varName => {
                    table += `<th>${varName}</th>`;
                });
                table += '</tr></thead><tbody>';
                rows.forEach(row => {
                    table += '<tr>';
                    variables.forEach(varName => {
                        table += `<td>${row[varName] || ''}</td>`;
                    });
                    table += '</tr>';
                });
                table += '</tbody></table>';
                // Hide the loading spinner once results are displayed
                queryResults.innerHTML = table; // Set results before hiding spinner
                hideLoading();
            })
            .catch(error => {
                console.error('Error fetching query results:', error);
                hideLoading();
            });
        });
    });
});