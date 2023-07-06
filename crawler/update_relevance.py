"""
This script updates the relevance of all documents in the database.
"""
from playhouse.shortcuts import model_to_dict

from crawler import utils
from crawler.sql_models.document import Document
from crawler.worker.document_relevance import is_document_relevant
from crawler.worker.url_relevance import URL

LOG = utils.get_logger(__name__)


def update_relevance_of_documents_in_database():
    """
    Update erlevance of documents in database
    """
    updated = 0
    LOG.info(f"Starting to update relevance of documents in database.")
    total =  Document.select().count()
    LOG.info(f"Count {total}. This might take a while!")
    for document in Document.select().iterator():
        url = document.job["url"]
        try:
            document.relevant = is_document_relevant(URL(url), document)
            LOG.info(f"[{updated}/{total}] Relevance {document.relevant} of {url}")
            document.save()
            updated += 1
        except Exception as e:
            LOG.info("Error while updating relevant of document: " + url)
            LOG.info(e)


if __name__ == '__main__':
    update_relevance_of_documents_in_database()
