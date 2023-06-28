"""
This module contains the main crawling logic.
"""
import json
import os
import random
import time

import requests
from dotenv import load_dotenv
from playhouse.shortcuts import model_to_dict
from requests.adapters import HTTPAdapter, Retry
from requests_html import HTMLSession

from crawler import utils, relevance_classification
from crawler.models.document import Document
from crawler.models.job import Job

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

    def __init__(self, job: Job):
        """Initialize the Crawler object with a job to crawl.

        Args:
            job (Job): The job representing the URL to be crawled.
        """
        self.job: Job = job

    def generate_document_from_html(self, html: str, links: list[str]) -> Document:
        """Generate a Document object from the HTML content of a crawled page.

        Args:
            html (object): Response's text.
            links (list[str]): A list of links harvested from the crawled page.
        Returns:
            Document: The generated Document object.
        """
        title, body = utils.text.get_title_and_body_from_html(html)
        title_tokens = utils.text.tokenize(title)
        body_tokens = utils.text.tokenize(body)
        relevant_links = [url for url in links if relevance_classification.is_url_relevant(url)]
        return Document(url=self.job.url,
                        server=utils.url.get_server_name_from_url(self.job.url),
                        title=title,
                        body=body,
                        title_tokens=json.dumps(title_tokens),
                        body_tokens=json.dumps(body_tokens),
                        all_harvested_links=json.dumps(links),
                        relevant_links=json.dumps(relevant_links),
                        job=self.job)

    def try_to_obtain_static_website_html(self):
        """Send an HTTP request to the URL of the job.

        Returns:
            requests.Response: The response object of the HTTP request.

        Raises:
            Exception: If the response is not successful or the content type is not HTML.
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
        """Send an HTTP request to the URL of the job.

        Returns:
            requests.Response: The response object of the HTTP request.

        Raises:
            Exception: If the response is not successful or the content type is not HTML.
        """
        session = HTMLSession()
        session.mount('http://', HTTPAdapter(max_retries=RETRIES))
        session.mount('https://', HTTPAdapter(max_retries=RETRIES))
        response = session.get(self.job.url, timeout=CRAWL_TIMEOUT)
        response.html.render(timeout=CRAWL_RENDER_TIMEOUT)
        if not response.ok:
            raise Exception(
                f"Error while rendering dynamic website. Response not ok: {response} for URL: {self.job.url}")
        if "html" not in (data_type := response.headers.get("Content-Type")):
            raise Exception(
                f"Error while rendering dynamic website. Only accept HTML. Got {data_type} for URL: {self.job.url}")
        return response

    def crawl_assume_website_is_static(self) -> Document:
        """Try to assume that the website is static and crawl it.

        Returns:
            Document: The crawled Document object.
        """
        response = self.try_to_obtain_static_website_html()
        html = response.text
        links = utils.url.get_absolute_links(html, self.job.url)
        new_document = self.generate_document_from_html(html, links)
        relevance_classification.is_document_relevant(new_document)
        return new_document

    def crawl_assume_website_is_dynamic(self) -> Document:
        """
        Try to assume that the website is dynamic and crawl it.
        :return:
            Document: The crawled Document object.
        """
        response = self.try_to_obtain_static_website_html()
        html = response.text
        links = utils.url.get_absolute_links(html, self.job.url)
        new_document = self.generate_document_from_html(html, links)
        new_document.relevant = relevance_classification.is_document_relevant(new_document)
        return new_document

    def crawl(self) -> Document:
        """Perform the crawling process for the given job.

        This procedure tries to crawl the website at least twice.
        One assuming the website is static and one assuming it is dynamic.
        The static crawling is cheaper but less accurate.
        The dynamic crawling is more expensive but more accurate.

        If the static crawling is successful, the dynamic crawling is not performed.
        A static crawling is succesful if the website is relevant to Tuebingen and in english.

        Since we use two different libraries, this code is a bit messy.

        Returns:
            The crawled document.
        """
        if relevance_classification.is_job_relevant(self.job):
            new_document = None

            try:  # First, try a cheaper static version.
                new_document = self.crawl_assume_website_is_static()
            except Exception as exception:
                LOG.error(f"{str(exception)}")

            if new_document is None or not new_document.relevant:
                try:  # If not successful, try static version with vanilla requests.
                    # Wait a bit to not get blocked.
                    time.sleep(random.randint(*CRAWL_RANDOM_SLEEP_INTERVAL))
                    new_document = self.crawl_assume_website_is_dynamic()
                except Exception as exception:
                    LOG.error(f"{str(exception)}")

            if new_document is not None:  # Retrieved document successfully.
                if new_document.relevant:  # Document is relevant. Queue its children.
                    return new_document
                # Document is not relevant. Do not queue its children.
                return new_document
        else:
            LOG.info(f"Job {self.job.url} is not relevant.")
        return None  # Document could not be retrieved.
