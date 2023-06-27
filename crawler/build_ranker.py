"""
crawler/build_ranker.py

This script.js builds a ranker model using the TF-IDF vectorizer and relevant document tokens.
The ranker model is trained using the TfidfVectorizer from scikit-learn.

Usage:
    python3 build_ranker.py
"""
import json
import os

import networkx as nx
from dotenv import load_dotenv
from numpy.typing import ArrayLike
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

from crawler import utils
from crawler.models import Document

load_dotenv()

TFIDF_VECTORIZER_FILE = os.getenv("TFIDF_VECTORIZER_FILE")
TFIDF_NGRAM_RANGE = tuple(json.loads(os.getenv("TFIDF_NGRAM_RANGE")))
LOG = utils.get_logger(__name__, os.getenv("BUILD_RANKER_LOG_FILE"))


class DocumentStreamer:
    """
    A class to stream sentences from database to avoid eager loading.
    """

    def stream(self):
        """
        Stream tokens from relevant documents.
        :return: a generator
        """
        if self.ids is None:
            for doc in Document.select().where(Document.relevant == True).iterator():
                yield doc
        else:
            for doc_id in self.ids:
                doc = Document.get_by_id(doc_id)
                yield doc

    def __init__(self, ids: ArrayLike = None):
        """
        Stream sentences from relevant documents.

        Args:
            ids (list[int] | np.array): List of document IDs.
        """
        self.ids = ids
        self.generator = self.stream()

    def __iter__(self):
        """
        Reset the generator and return the iterator object.

        Returns:
            Streams: Iterator object for streaming sentences.
        """
        self.generator = self.stream()
        return self

    def __next__(self):
        """
        Get the next sentence from the generator.

        Returns:
            str: Concatenated sentence from a relevant document.

        Raises:
            StopIteration: If there are no more sentences to yield.
        """
        result = next(self.generator)
        if result is None:
            raise StopIteration
        return result


class DocumentTokensStreamer(DocumentStreamer):
    """
    A class to stream sentences from database to avoid eager loading.
    """

    def stream(self):
        """
        Stream tokens from relevant documents.
        :return: a generator
        """
        if self.ids is None:
            for doc in Document.select().where(Document.relevant == True).iterator():
                yield " ".join(doc.tokens_list)
        else:
            for doc_id in self.ids:
                doc = Document.get_by_id(doc_id)
                yield " ".join(doc.tokens_list)


def train_global_tf_idf():
    """
    Train the TF-IDF vectorizer using the relevant document tokens.

    The TF-IDF vectorizer is fitted on the concatenated sentences from the relevant documents.
    The fitted vectorizer is then saved as a pickle file.
    """
    LOG.info("Start build global tfidf")
    tfidf = TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE)
    LOG.info("Initialized build global tfidf")
    tfidf.fit(DocumentTokensStreamer())
    LOG.info("Fitted build global tfidf")
    utils.write_pickle_file(tfidf, TFIDF_VECTORIZER_FILE)
    LOG.info(f"Wrote TF-IDF file to {TFIDF_VECTORIZER_FILE}")


def construct_directed_link_graph_from_crawled_documents():
    """
    Construct a directed link graph from the crawled documents.

    The constructed graph will be saved as a pickle file.
    """
    graph = nx.DiGraph()
    for doc in tqdm(DocumentStreamer()):
        from_server = doc.job.server
        for url in doc.relevant_links_list:
            to_server = utils.get_domain_name_without_subdomain_and_suffix_from_url(
                url)
            if not graph.has_edge(
                    from_server, to_server) and from_server != to_server:
                graph.add_edge(
                    from_server,
                    to_server,
                    weight=1)  # Add edge with weight 1
            elif from_server != to_server:
                # Increment the weight of existing edge
                graph[from_server][to_server]['weight'] += 1
    utils.write_pickle_file(graph, os.getenv("DIRECTED_LINK_GRAPH_FILE"))


def construct_page_rank():
    """
    Construct the page rank of the servers.
    """
    network_graph = utils.read_pickle_file(os.getenv("DIRECTED_LINK_GRAPH_FILE"))
    ranking = nx.pagerank(network_graph,
                          max_iter=int(os.getenv("PAGERANK_MAX_ITER")),
                          personalization=json.loads(os.getenv("PAGERANK_PERSONALIZATION")))
    utils.write_json_file(ranking, os.getenv("PAGERANK_FILE"))


if __name__ == '__main__':
    construct_directed_link_graph_from_crawled_documents()
    construct_page_rank()
    train_global_tf_idf()
