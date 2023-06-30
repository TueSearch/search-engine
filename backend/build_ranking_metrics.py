"""
backend/build_ranker.py

This script.js builds a ranker model using the TF-IDF vectorizer and relevant document tokens.
The ranker model is trained using the TfidfVectorizer from scikit-learn.

Usage:
    python3 -m backend.build_ranker
"""
import json
import os

import networkx as nx
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

from crawler import utils
from backend.streamers import DocumentStreamer, DocumentTokensStreamer

load_dotenv()

TFIDF_VECTORIZER_FILE = os.getenv("TFIDF_VECTORIZER_FILE")
TFIDF_NGRAM_RANGE = tuple(json.loads(os.getenv("TFIDF_NGRAM_RANGE")))
LOG = utils.get_logger(__file__)


def train_global_tf_idf():
    """
    Train the TF-IDF vectorizer using the relevant document tokens.

    The TF-IDF vectorizer is fitted on the concatenated sentences from the relevant documents.
    The fitted vectorizer is then saved as a pickle file.
    """
    LOG.info("Start build global tfidf")
    tfidf = TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE)
    tfidf.fit(DocumentTokensStreamer())
    utils.io.write_pickle_file(tfidf, TFIDF_VECTORIZER_FILE)
    LOG.info(f"Wrote TF-IDF file to {TFIDF_VECTORIZER_FILE}")


def write_results_of_global_tf_idf_to_database():
    LOG.info("Start vectorize database's documents with the global TF-IDF to database")
    tfidf = utils.io.read_pickle_file(TFIDF_VECTORIZER_FILE)
    for document in tqdm(DocumentStreamer()):
        try:
            document.body_tfidf = tfidf.transform([" ".join(document.body_tokens)])[0]
            document.save()
        except Exception as e:
            LOG.error(f"Can not write results of global TF-IDF of one entry to database: {e}")
    LOG.info("Finished vectorize database's documents with the global TF-IDF to database")


def construct_directed_link_graph_from_crawled_documents():
    """
    Construct a directed link graph from the crawled documents.

    The constructed graph will be saved as a pickle file.
    """
    LOG.info("Start constructing directed link graph")
    graph = nx.DiGraph()
    for doc in tqdm(DocumentStreamer()):
        from_server = str(doc.job.server.name)
        for url in doc.links:
            to_server = utils.url.get_server_name_from_url(url)
            if not graph.has_edge(
                    from_server, to_server) and from_server != to_server:
                graph.add_edge(
                    from_server,
                    to_server,
                    weight=1)  # Add edge with weight 1
            elif from_server != to_server:
                # Increment the weight of existing edge
                graph[from_server][to_server]['weight'] += 1
    LOG.info("Finished constructing directed link graph")
    utils.io.write_pickle_file(graph, os.getenv("DIRECTED_LINK_GRAPH_FILE"))
    LOG.info("Wrote directed link graph")


def construct_page_rank():
    """
    Construct the page rank of the servers.
    """
    LOG.info("Start constructing page rank")
    network_graph = utils.io.read_pickle_file(os.getenv("DIRECTED_LINK_GRAPH_FILE"))
    ranking = nx.pagerank(network_graph,
                          max_iter=int(os.getenv("PAGERANK_MAX_ITER")),
                          personalization=json.loads(os.getenv("PAGERANK_PERSONALIZATION")))
    LOG.info("Finished constructing page rank")
    utils.io.write_json_file(ranking, os.getenv("PAGERANK_FILE"))
    LOG.info("Wrote page rank")


if __name__ == '__main__':
    # construct_directed_link_graph_from_crawled_documents()
    # construct_page_rank()
    train_global_tf_idf()
    write_results_of_global_tf_idf_to_database()
