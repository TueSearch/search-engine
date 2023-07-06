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
    n = 10
    top_20_servers = execute_query_and_return_objects(f"select * from servers order by total_done_jobs desc limit {n}")
    latest_20_rel_doc = execute_query_and_return_objects(f"select jobs.url, documents.body_tokens from documents join jobs where documents.job_id = jobs.id and documents.relevant = 1 order by documents.created_date desc limit {n}")
    latest_20_irrrel_doc = execute_query_and_return_objects(f"select jobs.url, documents.body_tokens from documents join jobs where documents.job_id = jobs.id and documents.relevant = 0 order by documents.created_date desc limit {n}")
    top_20_jobs = execute_query_and_return_objects(f"select * from jobs order by priority desc limit {n}")
    random_20_jobs = execute_query_and_return_objects(f"select * from jobs order by rand() limit {n}")

    return jsonify({
        'total_servers': Server.select().count(),
        'total_jobs': Job.select().count(),
        'total_done_jobs': Job.select().where(Job.done == 1).count(),
        'total_documents': Document.select().count(),
        'total_relevant_documents': Document.select().where(Document.relevant == 1).count(),
        f'top_{n}_servers': top_20_servers,
        f'latest_{n}_rel_doc': latest_20_rel_doc,
        f'latest_{n}_irrrel_doc': latest_20_irrrel_doc,
        f'top_{n}_jobs': top_20_jobs,
        f'random_{n}_jobs': random_20_jobs
    })


def main():
    """Start the Flask application."""
    app.run(debug=True, host="0.0.0.0", port=4002)


if __name__ == '__main__':
    main()
