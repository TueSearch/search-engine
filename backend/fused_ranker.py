from collections import defaultdict
from typing import Tuple, List, Dict

import numpy as np
from dotenv import load_dotenv

from backend.build_index import read_short_inverted_index
from backend.rankers.tfidf_ranker import TFIDFRanker
from crawler import utils
from crawler.sql_models.document import Document

load_dotenv()

LOG = utils.get_logger(__file__)


class FusedRanker:
    def __init__(self):
        pickled_index = read_short_inverted_index()
        self.indices = pickled_index[0]
        self.all_doc_ids = pickled_index[1]

    def get_matches_for_query_tokens(self, query_tokens: list[str]) -> dict[str, list[int]]:
        matches = defaultdict(list)
        for index_name, index in self.indices.items():
            for query_token in query_tokens:
                if query_token in index:
                    matches[index_name].extend(index[query_token])
        return matches

    def scores(self, query: str) -> tuple[list[str], dict[int, float]]:
        """
        Retrieves a ranking of document IDs based on global TF-IDF naive normalized distance.

        Args:
            query (str): The query string.

        Returns:
            list[int]: A list of document IDs, sorted by their ranking.

        """
        # Preprocess the query
        query_tokens = utils.text.advanced_tokenize_with_pos(query)
        # Get the document IDs that match the query tokens
        matched_ids = self.get_matches_for_query_tokens(query_tokens)
        # Scores of the documents based on the TF-IDF
        return query_tokens, TFIDFRanker(query_tokens, matched_ids).scores()

    def process_query(self, query: str, page=0, page_size=10) -> (list[str], list[Document]):
        """
        Rank the documents based on a query.

        Args:
            query (str): The query string.
            page (int): The page number of the results (default: 0).
            page_size (int): The number of results per page (default: 10).

        Returns:
            (list[str], list[Document]): Tokens of query for debugging and list of ranked documents.

        Note:
            This function assumes that the global TF-IDF vectorizer has been trained.

        Example:
            documents = rank("search query", page=0, page_size=10)
        """
        query_tokens, documents_id_mapped_to_scores = self.scores(query)
        # Convert the document_ids array to a list
        ranking = list(documents_id_mapped_to_scores.keys())
        ranking.sort(reverse=True, key=lambda x: documents_id_mapped_to_scores[x])
        # Retrieve the documents based on the ranked document IDs
        documents = Document.select().where(Document.id.in_(ranking)).paginate(page + 1, page_size)
        return query_tokens, list(documents)


if __name__ == '__main__':
    query = "the press in germany is bullshit"
    processed_query, docs = FusedRanker().process_query(query)
    print(processed_query)
    for doc in docs:
        print(doc)
