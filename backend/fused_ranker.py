"""
This module contains the FusedRanker class.
"""
from collections import defaultdict

from dotenv import load_dotenv

from backend.build_index import read_index_file
from backend.rankers.tfidf_ranker import TFIDFRanker
from crawler import utils
from crawler.sql_models.document import Document

load_dotenv()

LOG = utils.get_logger(__file__)


class FusedRanker:
    """
    This class builds a ranker model using the TF-IDF vectorizer
    and relevant document tokens.
    """

    def __init__(self):
        pickled_index = read_index_file()
        self.indices = pickled_index[0]
        self.all_doc_ids = pickled_index[1]

    def get_matches_for_query_tokens(self, query_tokens: list[str]) -> dict[str, list[int]]:
        """
        Returns the document IDs that match the query tokens.
        The document IDs are grouped by the index name.
        """
        matches = defaultdict(list)
        for index_name, index in self.indices.items():
            for query_token in query_tokens:
                if query_token in index:
                    matches[index_name].extend(index[query_token])
        return matches

    def scores(self, query: str) -> tuple[list[str], dict[int, float]]:
        """
        Returns the tokens of the query and the scores of the documents based on the TF-IDF.
        """
        # Preprocess the query
        query_tokens = utils.text.advanced_tokenize_with_pos(query)
        # Get the document IDs that match the query tokens
        matched_ids = self.get_matches_for_query_tokens(query_tokens)
        # Scores of the documents based on the TF-IDF
        return query_tokens, TFIDFRanker(query_tokens, matched_ids).scores()

    def process_query(self, query: str, page=0, page_size=10) -> (list[str], list[Document]):
        """
        Returns the tokens of the query and the documents that match the query.
        The documents are ranked based on the TF-IDF.
        """
        query_tokens, documents_id_mapped_to_scores = self.scores(query)
        # Convert the document_ids array to a list
        ranking = list(documents_id_mapped_to_scores.keys())
        ranking.sort(reverse=True, key=lambda x: documents_id_mapped_to_scores[x])
        # Retrieve the documents based on the ranked document IDs
        documents = Document.select().where(Document.id.in_(ranking)).paginate(page + 1, page_size)
        return query_tokens, list(documents)
