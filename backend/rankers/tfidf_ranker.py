"""
This module is responsible for ranking documents based on their TF-IDF scores.
"""
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.vector_spaces.tfidf import read_tfidf_vectorizers, Tfidf
from crawler import utils

LOG = utils.get_logger(__file__)

VECTORIZERS: dict[str, TfidfVectorizer] = read_tfidf_vectorizers()
VECTOR_SPACE_WEIGHTS = {"title": 10, "meta_description": 5, "meta_keywords": 5, "meta_author": 5, "h1": 10, "h2": 8,
                        "h3": 6, "h4": 4, "h5": 2,
                        "h6": 1, "body": 1
                        }


class TFIDFRanker:
    """
    This class is responsible for ranking documents based on their TF-IDF scores.
    """

    def __init__(self, query_tokens: list[str], matches_in_vector_spaces: dict[str, list[int]]):
        self.query_tokens = query_tokens
        self.matches_in_vector_spaces = matches_in_vector_spaces
        self.final_scores = defaultdict(float)

    @staticmethod
    def query_document_similarities_in_all_vector_spaces(query_vectors: list[np.array],
                                                         document_vectors: list[np.array]) -> np.array:
        """
        Returns the cosine similarities of the query and the document in all vector spaces.
        """
        return np.array([np.dot(query_vector, document_vector) for query_vector, document_vector in
                         zip(query_vectors, document_vectors)])

    @staticmethod
    def map_query_to_vector_spaces(query_tokens: list[str]) -> dict[str, np.array]:
        """
        Returns the query tokens mapped to the vector spaces.
        """
        ret = {}
        for name, vectorizer in VECTORIZERS.items():
            try:
                ret[name] = vectorizer.transform([" ".join(query_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming query into vector space '{name}': {exception}")
        return ret

    def update_scores_of_matches_with_new_vector_space(self,
                                                       query_vector: np.array,
                                                       matches: list[int],
                                                       vector_space_name: str):
        """
        Updates the scores of the matches with the new vector space.
        """
        tfidfs = Tfidf.select().where(Tfidf.id.in_(matches))
        weight = VECTOR_SPACE_WEIGHTS[vector_space_name]
        for tfidf in tfidfs:
            doc_vectors = tfidf.not_null_vectors()
            if vector_space_name in doc_vectors:
                doc_vector = doc_vectors[vector_space_name]
                LOG.info(
                    f"Cosine similarity of {query_vector.shape=}, {type(query_vector)=}, {doc_vector.shape=}, {type(doc_vector)=}")
                cosine_sim = query_vector.multiply(doc_vector).sum()
                LOG.info(f"{cosine_sim.shape=}, {type(cosine_sim)=}")
                self.final_scores[tfidf.id] += weight * cosine_sim

    def scores(self) -> dict[int, float]:
        """
        Returns the final scores of the documents.
        """
        query_vectors = self.map_query_to_vector_spaces(self.query_tokens)
        for vector_space_name, matches_in_vector_space in self.matches_in_vector_spaces.items():
            if vector_space_name in query_vectors:
                self.update_scores_of_matches_with_new_vector_space(query_vectors[vector_space_name],
                                                                    matches_in_vector_space,
                                                                    vector_space_name)
        return self.final_scores
