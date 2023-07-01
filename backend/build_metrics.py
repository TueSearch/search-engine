"""
backend/build_ranker.py

This script.js builds a ranker model using the TF-IDF vectorizer and relevant document tokens.
The ranker model is trained using the TfidfVectorizer from scikit-learn.

Usage:
    python3 -m backend.build_ranker
"""
from dotenv import load_dotenv

from backend.vector_spaces.tfidf import train_tf_idf_vectorizer, tfidf_vectorize_indexed_documents
from crawler import utils
from crawler.sql_models.base import connect_to_database

load_dotenv()

LOG = utils.get_logger(__file__)


def main():
    """
    Builds the ranker model.
    """
    connect_to_database()
    train_tf_idf_vectorizer()
    tfidf_vectorize_indexed_documents()


if __name__ == '__main__':
    main()
