"""
backend/build_ranker.py

This script.js builds a ranker model using the TF-IDF vectorizer and relevant document tokens.
The ranker model is trained using the TfidfVectorizer from scikit-learn.

Usage:
    python3 -m backend.build_ranker
"""
from dotenv import load_dotenv

from backend.rankers import page_rank
from backend.vector_spaces.lda import train_lda_vectorizer, lda_vectorize_indexed_documents
from backend.vector_spaces.tfidf import train_tfidf_vectorizer, tfidf_vectorize_indexed_documents
from crawler import utils
from crawler.sql_models.base import connect_to_database

load_dotenv()

LOG = utils.get_logger(__file__)


def main():
    """
    Builds the ranker model.
    """
    connect_to_database()

    train_tfidf_vectorizer()
    tfidf_vectorize_indexed_documents()

    train_lda_vectorizer()
    lda_vectorize_indexed_documents()

    page_rank.construct_directed_link_graph_from_crawled_documents()
    page_rank.construct_page_rank_of_servers_from_directed_graph()
    page_rank.update_page_rank_of_servers_in_database()


if __name__ == '__main__':
    main()
