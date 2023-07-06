"""
Mock up server without any connection to other module.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    """Mock up search"""
    query = request.args.get('q', '')
    if query:
        page = int(request.args.get('page', 0))
        page_size = int(request.args.get('page_size', 10))
        # Prepare the JSON response
        response = {
            'query': query,
            'query_tokens': ["example_TEST"],
            'page': page,
            'page_size': page_size,
            'results': []
        }

        for _ in range(page_size):
            result = {
                'title': "example",
                'body': "example",
                'url': "https://de.wikipedia.org/wiki/T%C3%BCbingen",
                'relevant': True
            }
            response['results'].append(result)

        return jsonify(response)
    return jsonify({'error': 'Invalid query'})


def main():
    """Start the Flask application."""
    app.run(debug=True, host="0.0.0.0", port=4001)


if __name__ == '__main__':
    main()
