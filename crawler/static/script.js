// script.js

// Wait for the DOM content to load
document.addEventListener('DOMContentLoaded', function() {
  // Get the search form and results container elements
  var searchForm = document.getElementById('searchForm');
  var resultsContainer = document.getElementById('resultsContainer');

  // Attach a submit event listener to the search form
  searchForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get the query input value
    var queryInput = document.getElementById('queryInput');
    var query = queryInput.value.trim();

    // Clear the results container
    resultsContainer.innerHTML = '';

    if (query !== '') {
      // Send a GET request to the search endpoint
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/search?q=' + encodeURIComponent(query), true);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var response = JSON.parse(xhr.responseText);
          displayResults(response);
        }
      };
      xhr.send();
    }
  });

  // Function to display the search results
  function displayResults(response) {
    var results = response.results;

    if (results.length === 0) {
      // No results found
      resultsContainer.innerHTML = '<p>No results found.</p>';
    } else {
      // Display each result
      for (var i = 0; i < results.length; i++) {
        var result = results[i];
        var resultItem = document.createElement('div');
        resultItem.className = 'result-item';

        var resultTitle = document.createElement('h2');
        resultTitle.className = 'result-title';
        resultTitle.textContent = result.title;

        var resultUrl = document.createElement('a');
        resultUrl.className = 'result-url';
        resultUrl.href = result.url;
        resultUrl.textContent = result.url;

        resultItem.appendChild(resultTitle);
        resultItem.appendChild(resultUrl);
        resultsContainer.appendChild(resultItem);
      }
    }
  }
});
