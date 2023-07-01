"""
This module contains the main crawling logic.
"""
import json
import os
import random
import time
import traceback

import requests
from dotenv import load_dotenv
from playhouse.shortcuts import model_to_dict
from requests.adapters import HTTPAdapter, Retry
from requests_html import HTMLSession

from crawler import utils
from crawler.sql_models.document import Document
from crawler.relevance_classification import url_relevance
from crawler.relevance_classification.url_relevance import URL
from crawler.relevance_classification.document_relevance import is_document_relevant
from crawler.sql_models.job import Job
import requests

load_dotenv()

CRAWL_LOG_FILE = os.getenv("CRAWL_LOG_FILE")
CRAWL_BATCH_SIZE = int(os.getenv("CRAWL_BATCH_SIZE"))
CRAWL_TIMEOUT = int(os.getenv("CRAWL_TIMEOUT"))
CRAWL_RENDER_TIMEOUT = int(os.getenv("CRAWL_RENDER_TIMEOUT"))
CRAWL_RETRIES = int(os.getenv("CRAWL_RETRIES"))
CRAWL_RETRIES_IF_STATUS = json.loads(os.getenv("CRAWL_RETRIES_IF_STATUS"))
CRAWL_BACKOFF_FACTOR = float(os.getenv("CRAWL_BACKOFF_FACTOR"))
CRAWL_RANDOM_SLEEP_INTERVAL = list(json.loads(
    os.getenv("CRAWL_RANDOM_SLEEP_INTERVAL")))
CRAWL_REDIRECTION_LIMIT = int(os.getenv("CRAWL_REDIRECTION_LIMIT"))
CRAWL_RAISE_ON_STATUS = bool(os.getenv("CRAWL_RAISE_ON_STATUS"))
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'DNT': '1',  # Do Not Track
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}
RETRIES = Retry(total=CRAWL_RETRIES,
                backoff_factor=CRAWL_BACKOFF_FACTOR,
                status_forcelist=CRAWL_RETRIES_IF_STATUS,
                redirect=CRAWL_REDIRECTION_LIMIT,
                raise_on_status=CRAWL_RAISE_ON_STATUS)
LOG = utils.get_logger(__file__)
random.seed(1)


class Crawler:
    """Represents a web crawler that retrieves a single page, classifies its relevance, and extracts information."""

    def __init__(self):
        self.url: str = ""

    def generate_document_from_html(self, html: str) -> (Document, list[URL]):
        document = utils.text.generate_text_document_from_html(html)
        document.relevant = is_document_relevant(document)
        urls = url_relevance.URL.get_links(document, self.url)
        urls = [url for url in urls if url.is_relevant]
        document.job_id = self.job.id
        return document, urls

    def try_to_obtain_static_website_html(self):
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=RETRIES))
        session.mount('https://', HTTPAdapter(max_retries=RETRIES))
        response = session.get(self.job.url, timeout=CRAWL_TIMEOUT, headers=HEADERS)
        if not response.ok:
            raise Exception(
                f"Error while rendering static website. Response not ok: {response} for URL: {self.job.url}")
        if "html" not in (data_type := response.headers.get("Content-Type")):
            raise Exception(
                f"Error while rendering static website. Only accept HTML. Got {data_type} for URL: {self.job.url}")
        return response

    def try_to_obtain_dynamic_website_html(self):
        session = HTMLSession()
        session.mount('http://', HTTPAdapter(max_retries=RETRIES))
        session.mount('https://', HTTPAdapter(max_retries=RETRIES))
        response = session.get(self.job.url, timeout=CRAWL_TIMEOUT, headers=HEADERS)
        response.html.render(timeout=CRAWL_RENDER_TIMEOUT)
        if not response.ok:
            raise Exception(
                f"Error while rendering dynamic website. Response not ok: {response} for URL: {self.job.url}")
        if "html" not in (data_type := response.headers.get("Content-Type")):
            raise Exception(
                f"Error while rendering dynamic website. Only accept HTML. Got {data_type} for URL: {self.job.url}")
        return response

    def crawl_assume_website_is_static(self) -> (Document, list[URL]):
        response = self.try_to_obtain_static_website_html()
        html = response.text
        new_document = self.generate_document_from_html(html)
        return new_document

    def crawl_assume_website_is_dynamic(self) -> (Document, list[URL]):
        response = self.try_to_obtain_dynamic_website_html()
        html = response.text
        new_document = self.generate_document_from_html(html)
        return new_document

    def crawl(self) -> (Document, list[URL]):
        new_document, urls = None, []
        try:  # First, try a cheaper static version.
            new_document, urls = self.crawl_assume_website_is_static()
        except Exception as exception:
            LOG.error(f"{str(exception)}")
            traceback.print_exc()

        if new_document is None or not new_document.relevant:
            time.sleep(random.randint(*CRAWL_RANDOM_SLEEP_INTERVAL))
            try:  # If not successful, try static version with vanilla requests.
                new_document, urls = self.crawl_assume_website_is_dynamic()
            except Exception as exception:
                LOG.error(f"{str(exception)}")
        return new_document, urls

    def loop(self):
        while True:
            self.job = requests.get("http://localhost:6000/reserve_job").json()
            self.job = self.job["url"]
            LOG.info("Retrieved new job: " + str(self.job))
            new_document, new_relevant_urls = self.crawl()
            new_jobs = Job.create_jobs_to_send_to_master(relevant_links=new_relevant_urls)
            new_document = model_to_dict(new_document)
            del new_document["created_date"]
            del new_document["last_time_changed"]
            new_document = json.dumps(new_document)
            requests.post(f"http://localhost:6000/save_crawling_results/{self.job.id}",
                          json={"new_document": new_document, "new_jobs": new_jobs})


def main():
    """
    Start the processes to crawl the jobs.
    """
    crawler = Crawler()
    crawler.loop()


if __name__ == '__main__':
    main()
