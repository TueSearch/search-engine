"""
API to retrieve quick statistic about the current data.
"""
from dotenv import load_dotenv
from crawler.sql_models.document import Document
from crawler.sql_models.job import Job
from crawler.sql_models.server import Server
from flask import Flask, jsonify
from crawler.sql_models.base import connect_to_database, execute_query_and_return_objects

load_dotenv()
app = Flask(__name__)
connect_to_database()
app.config['JSON_SORT_KEYS'] = False
app.json.sort_keys = False # https://stackoverflow.com/a/76032364

@app.route('/', methods=['GET'])
def statistic():
    top_20_servers = execute_query_and_return_objects("select * from servers order by total_done_jobs desc limit 20")
    return jsonify({
        'total_servers': Server.select().count(),
        'total_jobs': Job.select().count(),
        'total_done_jobs': Job.select().where(Job.done == 1).count(),
        'total_documents': Document.select().count(),
        'total_relevant_documents': Document.select().where(Document.relevant == 1).count(),
        'top_20_servers': top_20_servers
    })


def main():
    """Start the Flask application."""
    app.run(debug=True, host="0.0.0.0", port=4002)


if __name__ == '__main__':
    main()
