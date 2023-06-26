"""
This module implements a simple Flask application for searching and ranking documents.

It provides a basic web interface where users can enter a search query, and the application
will return ranked documents based on the query using the `rank()` function from the `crawler.rank` module.

The application exposes the following endpoints:
- GET /: Serves the index.html file as the frontend.
- GET /<path:path>: Serves all files in the static directory.
- GET /search: Handles search requests and returns ranked documents in JSON format.

Usage:
- Start the Flask application by running this script.
- Open a web browser and access http://localhost:5000/ to access the search interface.
"""

from flask import Flask, request, jsonify, send_from_directory
from crawler.rank import rank

app = Flask(__name__)


@app.route('/')
def index():
    """Serve the index.html file as the frontend."""
    return app.send_static_file('index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve all files in the static directory."""
    return send_from_directory('static', path)


@app.route('/search', methods=['GET'])
def search():
    """Handle the search request and return ranked documents."""
    query = request.args.get('q', '')  # Get the query parameter from the request

    if query:
        page = int(request.args.get('page', 0))  # Get the page parameter from the request
        page_size = int(request.args.get('page_size', 10))  # Get the page_size parameter from the request

        documents = rank(query, page=page, page_size=page_size)  # Call the rank() function to get ranked documents

        # Prepare the JSON response
        response = {
            'query': query,
            'page': page,
            'page_size': page_size,
            'results': []
        }

        for doc in documents:
            result = {
                'id': doc.id,
                'title': doc.title,
                'url': doc.url,
            }
            response['results'].append(result)

        return jsonify(response)
    return jsonify({'error': 'Invalid query'})


if __name__ == '__main__':
    app.run(debug=True)
