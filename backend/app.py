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
- Open a web browser and access http://localhost:4000/ to access the search interface.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from backend.fused_ranker import FusedRanker
from crawler.sql_models.base import connect_to_database

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
ranker = FusedRanker()


@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    """Handle the search request and return ranked documents."""
    query = request.args.get('q', '')  # Get the query parameter from the request
    if query:
        page = int(request.args.get('page', 0))  # Get the page parameter from the request
        page_size = int(request.args.get('page_size', 10))  # Get the page_size parameter from the request

        query_tokens, documents = ranker.process_query(query, page=page,
                                                       page_size=page_size)  # Call the rank() function to get ranked documents

        # Prepare the JSON response
        response = {
            'query': query,
            'query_tokens': query_tokens,
            'page': page,
            'page_size': page_size,
            'results': []
        }

        for doc in documents:
            result = {
                'title': doc.title,
                'body': doc.body,
                'url': doc.job['url'],
                'relevant': doc.relevant
            }
            response['results'].append(result)

        return jsonify(response)
    return jsonify({'error': 'Invalid query'})


def main():
    """Start the Flask application."""
    connect_to_database()
    app.run(debug=True, host="0.0.0.0", port=4000)


if __name__ == '__main__':
    main()
