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


class Indexer:
    def __init__(self):
        self.index = {
            "title": defaultdict(list),
            "meta_description": defaultdict(list),
            "meta_keywords": defaultdict(list),
            "meta_author": defaultdict(list),
            "h1": defaultdict(list),
            "h2": defaultdict(list),
            "h3": defaultdict(list),
            "h4": defaultdict(list),
            "h5": defaultdict(list),
            "h6": defaultdict(list),
            "body": defaultdict(list),
        }
        self.doc_ids = []

    def build_index(self):
        for document in tqdm(DocumentStreamer()):  # Iterate over the documents
            self.doc_ids.append(document.id)
            LOG.info(f"Indexing {document}")

            for token in document.title_tokens:
                self.index["title"][token].append(document.id)
            LOG.info("Indexed title")

            for token in document.meta_description_tokens:
                self.index["meta_description"][token].append(document.id)
            LOG.info("Indexed meta_description")

            for token in document.meta_keywords_tokens:
                self.index["meta_keywords"][token].append(document.id)
            LOG.info("Indexed meta_keywords")

            for token in document.meta_author_tokens:
                self.index["meta_author"][token].append(document.id)
            LOG.info("Indexed meta_author")

            for token in document.h1_tokens:
                self.index["h1"][token].append(document.id)
            LOG.info("Indexed h1")

            for token in document.h2_tokens:
                self.index["h2"][token].append(document.id)
            LOG.info("Indexed h2")

            for token in document.h3_tokens:
                self.index["h3"][token].append(document.id)
            LOG.info("Indexed h3")

            for token in document.h4_tokens:
                self.index["h4"][token].append(document.id)
            LOG.info("Indexed h4")

            for token in document.h5_tokens:
                self.index["h5"][token].append(document.id)
            LOG.info("Indexed h5")

            for token in document.h6_tokens:
                self.index["h6"][token].append(document.id)
            LOG.info("Indexed h6")

            for token in document.body:
                self.index["body"][token].append(document.id)
            LOG.info("Indexed body")

        LOG.info("Finished short partial index")
        utils.io.write_pickle_file((self.index, self.doc_ids), SHORT_INVERTED_INDEX_FILE)
        LOG.info(f"Wrote short index file to {SHORT_INVERTED_INDEX_FILE}")


def read_short_inverted_index() -> (defaultdict[str, dict[str, list[int]]], list[int]):
    return utils.io.read_pickle_file(SHORT_INVERTED_INDEX_FILE)


def main():
    """
    Main function to build the inverted index and save it as a pickle file.
    """
    Indexer().build_index()


if __name__ == '__main__':
    main()
