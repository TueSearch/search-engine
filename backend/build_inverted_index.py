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
import json
import os
from collections import defaultdict

from tqdm import tqdm
from dotenv import load_dotenv

from crawler import utils
from backend.streamers import DocumentStreamer

load_dotenv()
LOG = utils.get_logger(__file__)
INVERTED_INDEX_FILE = os.getenv("INVERTED_INDEX_FILE")
PARTIAL_INVERTED_INDEX_FILE = os.getenv("PARTIAL_INVERTED_INDEX_FILE")


def build_inverted_index():
    """
    Build an inverted index from the crawled documents.

    Returns:
        defaultdict: The inverted index mapping tokens to document IDs and token positions.

    Example of result:
        {
            "term a" -> [(doc_id_1, pos_1, pos_2, pos_3), (doc_id_2, pos_2, pos_4), ...],
            "term b" -> [(doc_id_5, pos_1, pos_2, pos_3), (doc_id_42, pos_6, pos_4), ...],
            ...
        }
    """
    LOG.info("Start building index")
    inverted_index = defaultdict(list)
    # Iterate over the documents
    for document in tqdm(DocumentStreamer()):
        tokens_position = defaultdict(list)

        # Iterate over the tokens and their positions in the document
        for token_position_in_document, token in enumerate(document.body_tokens):
            # Append the token position to the list of positions for the token
            tokens_position[token].append(token_position_in_document)

        # Add the token positions to the inverted index
        for token, positions in tokens_position.items():
            # Append the document ID and token positions to the list of
            # postings for the token
            inverted_index[token].append((document.id, *positions))

    LOG.info("Finished building index")
    utils.io.write_pickle_file(inverted_index, INVERTED_INDEX_FILE)
    LOG.info(f"Wrote index file to {INVERTED_INDEX_FILE}")


def build_partial_inverted_index():
    """
    Build an inverted index from the crawled documents.

    Returns:
        defaultdict: The inverted index mapping tokens to document IDs and token positions.

    Example of result:
        {
            "term a" -> [doc_id_1, doc_id_2, ...],
            "term b" -> [doc_id_5, doc_id_42, ...],
            ...
        }
    """
    LOG.info("Start building partial index")
    inverted_index = defaultdict(list)
    # Iterate over the documents
    for document in tqdm(DocumentStreamer()):
        # Iterate over the tokens and their positions in the document
        for token in document.body_tokens:
            inverted_index[token].append(document.id)

    LOG.info("Finished building partial index")
    utils.io.write_pickle_file(inverted_index, PARTIAL_INVERTED_INDEX_FILE)
    LOG.info(f"Wrote partial index file to {PARTIAL_INVERTED_INDEX_FILE}")


def main():
    """
    Main function to build the inverted index and save it as a pickle file.
    """
    build_inverted_index()
    build_partial_inverted_index()


if __name__ == '__main__':
    main()
