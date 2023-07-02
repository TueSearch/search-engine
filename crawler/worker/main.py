"""
This module contains the main crawling logic.
"""
import argparse
import json
import math
import os
import random
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
CRAWL_RENDER_TIMEOUT = int(os.getenv("CRAWL_RENDER_TIMEOUT"))
CRAWL_RETRIES = int(os.getenv("CRAWL_RETRIES"))
CRAWL_RETRIES_IF_STATUS = json.loads(os.getenv("CRAWL_RETRIES_IF_STATUS"))
CRAWL_BACKOFF_FACTOR = float(os.getenv("CRAWL_BACKOFF_FACTOR"))
CRAWL_REDIRECTION_LIMIT = int(os.getenv("CRAWL_REDIRECTION_LIMIT"))
CRAWL_RAISE_ON_STATUS = bool(os.getenv("CRAWL_RAISE_ON_STATUS"))
CRAWL_TIMEOUT = int(os.getenv("CRAWL_TIMEOUT"))
CRAWLER_WORKER_TIMEOUT = int(os.getenv("CRAWLER_WORKER_TIMEOUT"))
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
CRAWL_WORKER_BATCH_SIZE = int(os.getenv("CRAWL_WORKER_BATCH_SIZE"))


class Crawler:
    """
    Crawler class.
    """

    def __init__(self):
        self.url: str = ""
        self.job_buffer: list[dotdict] = []
        self.current_job: dotdict = None
        self.new_document: dotdict = None
        self.new_relevant_urls: list = None
        self.new_jobs: list = None
        self.crawled_count: int = 0

    def generate_document_from_html(self, html: str) -> (Document, list[URL]):
        """
        Generate a document from the HTML of a website.
        """
        document = utils.text.generate_text_document_from_html(html)
        document.relevant = is_document_relevant(document)
        urls = url_relevance.URL.get_links(document, self.url)
        urls = [url for url in urls if url.is_relevant]
        document.job_id = self.current_job.id
        return document, urls

    def try_to_obtain_static_website_html(self):
        """
        Try to obtain the HTML of a static website.
        """
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=RETRIES))
        session.mount('https://', HTTPAdapter(max_retries=RETRIES))
        response = session.get(self.current_job.url, timeout=CRAWL_TIMEOUT, headers=HEADERS)
        if not response.ok:
            raise Exception(
                f"Error while rendering static website. Response not ok: {response} for URL: {self.current_job.url}")
        if "html" not in (data_type := response.headers.get("Content-Type")):
            raise Exception(
                f"Error while rendering static website. Only accept HTML. Got {data_type} for URL: {self.current_job.url}")
        return response

    def try_to_obtain_dynamic_website_html(self):
        """
        Try to obtain the HTML of a dynamic website.
        """
        session = HTMLSession()
        session.mount('http://', HTTPAdapter(max_retries=RETRIES))
        session.mount('https://', HTTPAdapter(max_retries=RETRIES))
        response = session.get(self.current_job.url, timeout=CRAWL_TIMEOUT, headers=HEADERS)
        response.html.render(timeout=CRAWL_RENDER_TIMEOUT)
        if not response.ok:
            raise Exception(
                f"Error while rendering dynamic website. Response not ok: {response} for URL: {self.current_job.url}")
        if "html" not in (data_type := response.headers.get("Content-Type")):
            raise Exception(
                f"Error while rendering dynamic website. Only accept HTML. Got {data_type} for URL: {self.current_job.url}")
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
            try:  # If not successful, try static version with vanilla requests.
                new_document, urls = self.crawl_assume_website_is_dynamic()
            except Exception as exception:
                LOG.error(f"{str(exception)}")
        return new_document, urls

    def get_job(self) -> dotdict:
        """
        Get a new job from the crawler manager.
        """
        if len(self.job_buffer) == 0:
            answer = requests.get(
                f"{CRAWLER_MANAGER_HOST}/get_job/{CRAWL_WORKER_BATCH_SIZE}?pw={CRAWLER_MANAGER_PASSWORD}",
                timeout=CRAWLER_WORKER_TIMEOUT)
            job_buffer = answer.json()
            for job in job_buffer:
                self.job_buffer.append(dotdict(json.loads(job)))
        return self.job_buffer.pop()

    def save_crawling_results(self, json_new_document: str, json_new_jobs: str):
        """
        Store the job in the database.
        """
        url = f"{CRAWLER_MANAGER_HOST}/save_crawling_results/{self.current_job.id}?pw={CRAWLER_MANAGER_PASSWORD}"
        response = requests.post(url,
                                 json={"new_document": json_new_document, "new_jobs": json_new_jobs},
                                 timeout=CRAWLER_WORKER_TIMEOUT)
        LOG.info(f"Manager answered to save_crawling_results: {response.text}")

    def mark_job_as_failed(self):
        """
        Mark the job as failed in the database.
        """
        response = requests.post(
            f"{CRAWLER_MANAGER_HOST}/mark_job_as_fail/{self.current_job.id}?pw={CRAWLER_MANAGER_PASSWORD}",
            timeout=CRAWLER_WORKER_TIMEOUT)
        LOG.info(f"Manager answered to mark_job_as_fail: {response.text}")

    def loop(self, number_of_documents_to_be_crawled: int):
        """
        Loop over the crawler, retrieving new jobs from the crawler manager,
        crawling them, and sending the results back.
        """
        while self.crawled_count < number_of_documents_to_be_crawled:
            try:
                if self.current_job is not None:
                    self.current_job = self.get_job()
                LOG.info(f"Retrieved new job: {self.current_job}")
                if self.new_document is None or self.new_jobs is None:
                    self.new_document, self.new_relevant_urls = self.crawl()
                if self.new_document:
                    self.new_jobs = Job.create_jobs_from_worker_to_master(relevant_links=self.new_relevant_urls)
                    self.new_document = json.dumps(model_to_dict(self.new_document))
                    try:
                        self.save_crawling_results(self.new_document, self.new_jobs)
                        self.crawled_count += 1
                        self.new_jobs = None
                        self.new_document = None
                        self.new_relevant_urls = None
                    except Exception as exception:
                        LOG.error(f"Error while sending back to master: {exception} Try again")
                else:
                    try:
                        self.mark_job_as_failed()
                        self.new_relevant_urls = None
                    except Exception as e:
                        LOG.error(f"Error while marking job as failed: {e}")
            except Exception as exception:
                LOG.error(f"Unexpected error: {str(exception)}")
                continue


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
