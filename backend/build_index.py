"""
backend/build_inverted_index.py

This script builds an inverted index from the crawled documents.
The inverted index maps tokens to document IDs and token positions.

This script.js fetches the crawled documents from the models, processes
the tokenized text, and constructs the inverted index. The resulting
inverted index is then saved as a pickle file for later use.

Usage:
    python3 backend/build_inverted_index.py
"""
import os
from collections import defaultdict

from tqdm import tqdm
from dotenv import load_dotenv

from crawler import utils
from backend.streamers import DocumentStreamer

load_dotenv()
LOG = utils.get_logger(__file__)
SHORT_INVERTED_INDEX_FILE = os.getenv("SHORT_INVERTED_INDEX_FILE")


def build_short_inverted_index():
    """
    Build an inverted index from the crawled documents.

    Returns:
        defaultdict: The inverted index mapping tokens to document IDs and token positions.

    Example of result:
        (
            {
                "term a" -> [doc_id_1, doc_id_2, ...],
                "term b" -> [doc_id_5, doc_id_42, ...],
                ...
            },
            [doc_id_1, doc_id_2, doc_id_5, doc_id_42, ...]
        )
    """
    LOG.info("Start short partial index")
    inverted_index = defaultdict(list)
    doc_ids = []
    # Iterate over the documents
    for document in tqdm(DocumentStreamer()):
        LOG.info(f"Indexing {document}")
        # Iterate over the tokens and their positions in the document
        for token in document.body_tokens:
            inverted_index[token].append(document.id)
        doc_ids.append(document.id)
    LOG.info("Finished short partial index")
    utils.io.write_pickle_file((inverted_index, doc_ids), SHORT_INVERTED_INDEX_FILE)
    LOG.info(f"Wrote short index file to {SHORT_INVERTED_INDEX_FILE}")


def read_short_inverted_index():
    return utils.io.read_pickle_file(SHORT_INVERTED_INDEX_FILE)


def main():
    """
    Main function to build the inverted index and save it as a pickle file.
    """
    build_short_inverted_index()


if __name__ == '__main__':
    main()
