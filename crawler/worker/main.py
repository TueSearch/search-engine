"""
This module contains the main crawling logic.
"""
import argparse
import json
import math
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
from crawler.relevance_classification import url_relevance
from crawler.relevance_classification.document_relevance import is_document_relevant
from crawler.relevance_classification.url_relevance import URL
from crawler.sql_models.base import dotdict
from crawler.sql_models.document import Document
from crawler.sql_models.job import Job

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

CRAWLER_MANAGER_PORT = int(os.getenv("CRAWLER_MANAGER_PORT"))
CRAWLER_MANAGER_PASSWORD = os.getenv("CRAWLER_MANAGER_PASSWORD")
CRAWLER_MANAGER_HOST = os.getenv("CRAWLER_MANAGER_HOST")


class Crawler:
    """
    Crawler class.
    """

    def __init__(self):
        self.url: str = ""
        self.job: dotdict = None

    def generate_document_from_html(self, html: str) -> (Document, list[URL]):
        """
        Generate a document from the HTML of a website.
        """
        document = utils.text.generate_text_document_from_html(html)
        document.relevant = is_document_relevant(document)
        urls = url_relevance.URL.get_links(document, self.url)
        urls = [url for url in urls if url.is_relevant]
        document.job_id = self.job.id
        return document, urls

    def try_to_obtain_static_website_html(self):
        """
        Try to obtain the HTML of a static website.
        """
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
        """
        Try to obtain the HTML of a dynamic website.
        """
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
        """
        Crawl the website, assuming it is static.
        """
        response = self.try_to_obtain_static_website_html()
        html = response.text
        new_document = self.generate_document_from_html(html)
        return new_document

    def crawl_assume_website_is_dynamic(self) -> (Document, list[URL]):
        """
        Crawl the website, assuming it is dynamic.
        """
        response = self.try_to_obtain_dynamic_website_html()
        html = response.text
        new_document = self.generate_document_from_html(html)
        return new_document

    def crawl(self) -> (Document, list[URL]):
        """
        Crawl the website, first assuming it is static, then assuming it is dynamic.
        """
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

    @staticmethod
    def get_job() -> dotdict:
        """
        Get a new job from the crawler manager.
        """
        answer = requests.get(
            f"{CRAWLER_MANAGER_HOST}/get_job?pw={CRAWLER_MANAGER_PASSWORD}",
            timeout=CRAWL_TIMEOUT)
        return dotdict(answer.json())

    def store_results(self, json_new_document: str, json_new_jobs: str):
        """
        Store the job in the database.
        """
        url = f"{CRAWLER_MANAGER_HOST}/save_crawling_results/{self.job.id}?pw={CRAWLER_MANAGER_PASSWORD}"
        requests.post(url, json={"new_document": json_new_document, "new_jobs": json_new_jobs})

    def mark_job_as_failed(self):
        """
        Mark the job as failed in the database.
        """
        requests.post(
            f"{CRAWLER_MANAGER_HOST}/mark_job_as_fail/{self.job.id}?pw={CRAWLER_MANAGER_PASSWORD}")

    def loop(self, number_of_documents_to_be_crawled: int):
        """
        Loop over the crawler, retrieving new jobs from the crawler manager,
        crawling them, and sending the results back.
        """
        i = 0
        while i < number_of_documents_to_be_crawled:
            i += 1
            self.job = self.get_job()
            LOG.info(f"Retrieved new job: {self.job}")
            new_document, new_relevant_urls = self.crawl()
            if new_document:
                new_jobs = Job.create_jobs_from_worker_to_master(relevant_links=new_relevant_urls)
                new_document = json.dumps(model_to_dict(new_document))
                self.store_results(new_document, new_jobs)
            else:
                self.mark_job_as_failed()


def main():
    """
    Start the processes to crawl the jobs.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', type=int, help='Number of rounds for the loop', default=math.inf)
    args = parser.parse_args()
    crawler = Crawler()
    crawler.loop(args.n)


if __name__ == '__main__':
    main()