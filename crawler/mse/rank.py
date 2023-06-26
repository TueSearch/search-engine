'''
The `rank` module provides functionality for ranking items based on a given metric or scoring mechanism.
'''

import os
from collections import defaultdict

import numpy as np
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

from mse import utils
from mse.build_ranker import DocumentTokensStreamer
from mse.models import Document

load_dotenv()

TFIDF_VECTORIZER_FILE = os.getenv("TFIDF_VECTORIZER_FILE")
TFIDF_VECTORIZER = utils.read_pickle_file(TFIDF_VECTORIZER_FILE)
INVERTED_INDEX_FILE = os.getenv("INVERTED_INDEX_FILE")
INVERTED_INDEX = utils.read_pickle_file(INVERTED_INDEX_FILE)
LOG = utils.get_logger(__name__)


def get_matches_for_tokens(tokens: list[str]) -> defaultdict[str, list]:
    """
    Return the document IDs for the documents matching the query.

    Args:
        tokens (str): The query to search for

    Returns:
        list: The list of document IDs matching the query

    Example of result:
        {
            "token1" -> [(doc_id_1, pos_1, pos_2, pos_3),(doc_id_2, pos_2, pos_4),...],
            "token2" -> [(doc_id_5, pos_1, pos_2, pos_3),(doc_id_42, pos_6, pos_4),...],
            ...
        }
    """
    token_matches = defaultdict(list)
    for token in tokens:
        token_matches[token].extend(INVERTED_INDEX[token])
    return token_matches


def get_global_tfidf_naive_norm_distance_ranking(query: str) -> np.array:
    """
    Retrieves a ranking of document IDs based on global TF-IDF naive normalized distance.

    Args:
        query (str): The query string.

    Returns:
        list[int]: A list of document IDs, sorted by their ranking.

    """
    # Preprocess the query
    query_tokens = utils.preprocess_text_and_tokenize(query)
    LOG.info(f"query_tokens: {query_tokens}")
    preprocessed_query = " ".join(query_tokens)

    # Get the document IDs for the documents matching the query
    matching_data_structure = get_matches_for_tokens(query_tokens)
    matched_document_ids = []
    for matched_documents in matching_data_structure.values():
        for matched_document in matched_documents:
            matched_document_ids.append(matched_document[0])
    matched_document_ids = np.asarray(matched_document_ids, dtype=np.int32)
    LOG.info(f"Matched: {matched_document_ids}")

    # Get the TF-IDF vectors for the query
    query_vector = TFIDF_VECTORIZER.transform([preprocessed_query])

    # Compute cosine similarities between the query vector and document vectors
    similarities = cosine_similarity(query_vector, TFIDF_VECTORIZER.transform(
        DocumentTokensStreamer(matched_document_ids)), dense_output=True)[0]

    # Create a dictionary to store document ranks
    return matched_document_ids[np.argsort(similarities)[::-1]]


def rank(query: str, page=0, page_size=10) -> list[Document]:
    """
    Rank the documents based on a query.

    Args:
        query (str): The query string.
        page (int): The page number of the results (default: 0).
        page_size (int): The number of results per page (default: 10).

    Returns:
        list[Document]: List of ranked documents.

    Note:
        This function assumes that the global TF-IDF vectorizer has been trained.

    Example:
        documents = rank("search query", page=0, page_size=10)
    """
    document_ids: np.array = get_global_tfidf_naive_norm_distance_ranking(query)
    # Convert the document_ids array to a list
    document_ids = document_ids.tolist()
    # Retrieve the documents based on the ranked document IDs
    documents = Document.select().where(
        Document.id.in_(document_ids)).paginate(
        page + 1, page_size)
    return list(documents)


if __name__ == '__main__':
    for doc in rank("ai/ml"):
        print(doc)
