"""
crawler/crawl.py - SERP Fetching


The `crawl` module is responsible for crawling web pages and extracting relevant information.

Crawler Workflow:
- The crawler follows a Breadth-First Search (BFS) approach to explore web pages.
It starts by retrieving a batch of jobs from the database using the `get_jobs_from_database_to_crawl` function.
Each job represents a URL to be crawled. The batch size is determined by the `CRAWL_BATCH_SIZE` constant.

- For each job in the batch, a separate process is created to crawl the web page asynchronously.
The crawling process is performed by the `Crawler` class. It sends an HTTP request to the URL,
using the `http_request` method, and retrieves the HTML content of the page.
If the response is successful and the content type is HTML, the HTML is parsed to generate a `Document` object
using the `generate_document_from_html` method.

- The `Document` object represents the crawled web page and contains various attributes such as the HTML content,
extracted text, tokens, and harvested links. The relevance of the document is then classified using the
`classify_document_relevance` method, which checks if the document is relevant to the target criteria.
The classification considers factors such as the presence of relevant keywords in the document, URL relevance,
and English language content.

- If the document is classified as relevant, the `harvest_jobs_from_relevant_document` method is called to extract
additional jobs from the relevant links found on the page. These new jobs represent URLs to be crawled
in future iterations.

- After crawling all the jobs in the batch, the crawled documents and new jobs are stored in the database. If a document
is relevant, it is saved in the `document` table, and the new jobs are inserted into the `job` table using the
`Job.insert_many` method. Duplicate jobs are ignored using the `on_conflict_ignore` clause.

- The crawling process continues until there are no more jobs to crawl. Each iteration fetches a new batch of jobs from
the database and processes them in parallel to accelerate the crawling process without overloading a single server.

Usage:
    python3 crawler/crawl.py --bfs_layer=<nr, default = use database's minimal bfs layer.>
"""
import argparse
import json
import math
import multiprocessing
import os
import random
import time
from collections import defaultdict

import peewee
import requests
from dotenv import load_dotenv
from peewee import SQL, fn
from playhouse.shortcuts import model_to_dict
from requests.adapters import HTTPAdapter, Retry
from requests_html import HTMLSession

from crawler import utilities
from crawler import utils
from crawler.models import DATABASE, Document, Job

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
LOG = utils.get_logger(__name__, CRAWL_LOG_FILE)
random.seed(1)


class PriorityQueue:
    """
    Manage which URL should be crawled as next.
    """

    def __init__(self, bfs_layer: int = None):
        """
        Initializes a priority queue for job scheduling.

        Args:
            bfs_layer (int, optional): The breadth-first search (BFS) layer to consider. If not specified,
                the front tier is used by default.
        """
        self.bfs_layer = bfs_layer

    def get_layer_to_crawl(self) -> int:
        """
        Retrieves the BFS layer to crawl.

        Returns:
            int: The BFS layer to crawl.
        """
        if self.bfs_layer is None:
            return Job.select(Job.bfs_layer).where(Job.done == False).distinct().order_by(Job.bfs_layer).limit(1)[
                0].bfs_layer  # Use front tier if no bfs layer is specified
        return self.bfs_layer

    @staticmethod
    def get_servers_by_highest_success_rate(_) -> list[str]:
        """
        Retrieves the servers with the highest success rates based on job success rate.

        Returns:
            list[str]: A list of server names, sorted by success rate.
        """
        success_rate = Job.select(Job.server,
                                  fn.COUNT(Job.id).alias('total_count'),
                                  fn.SUM(
                                      Job.done.cast('SIGNED INTEGER')).alias('total_done_count'),
                                  fn.SUM(Job.success.cast('SIGNED INTEGER')).alias('success_done_count')).where(
            (Job.done == True)).group_by(Job.server).alias('subquery')

        query = (
            Job
            .select(
                success_rate.c.server,
                (success_rate.c.success_done_count /
                 success_rate.c.total_done_count).alias('success_percent')
            ).where((success_rate.c.total_count - success_rate.c.success_done_count > 0))
            .from_(success_rate)
            .order_by(SQL('success_percent').desc())
        )

        servers = [job.server for job in query]
        LOG.info("#" * 50)
        LOG.info("# New batch.")
        LOG.info("# Sort priority queue by success chance.")
        return servers

    @staticmethod
    def get_servers_by_page_rank(bfs_layer: int) -> list[str]:
        """
        Retrieves the servers to crawl based on page rank, if available.

        Args:
            bfs_layer (int): The BFS layer to consider.

        Returns:
            list[str]: A list of server names, sorted by page rank.
        """
        servers = Job.select(
            Job.server).where(
            (Job.done == False) & (
                    Job.bfs_layer == bfs_layer)).distinct().limit()
        servers = [job.server for job in servers]
        page_rank = defaultdict(
            int, utils.read_json_file(
                os.getenv("PAGERANK_FILE")))
        servers = sorted(
            servers,
            key=lambda server: page_rank[server],
            reverse=True)
        servers = servers[:CRAWL_BATCH_SIZE]
        LOG.info("#" * 50)
        LOG.info("# New batch.")
        LOG.info("# Page rank exists. Sort priority queue by page rank.")
        return servers

    @staticmethod
    def get_servers_by_random(bfs_layer: int) -> list[str]:
        """
        Retrieves servers to crawl by random sorting.

        Args:
            bfs_layer (int): The BFS layer to consider.

        Returns:
            list[str]: A list of server names, sorted randomly.
        """
        servers = Job.select(Job.server).where((Job.done == False) & (Job.bfs_layer == bfs_layer)) \
            .order_by(fn.Rand()).distinct().limit(CRAWL_BATCH_SIZE)
        servers = [job.server for job in servers]
        LOG.info("#" * 50)
        LOG.info("# New batch.")
        LOG.info("# Sort priority randomly.")
        return servers

    def get_jobs_from_database_to_crawl(self) -> list[Job]:
        """
        Retrieves a list of jobs from the database to be crawled.

        Returns:
            list[Job]: A list of Job objects representing the URLs to be crawled.
        """
        bfs_layer = self.get_layer_to_crawl()
        jobs_to_be_crawled = []  # Select jobs that are not done in the specified bfs layer
        for server in self.get_servers_by_random(bfs_layer):
            next_job = Job.select().where(
                (Job.done == False) & (Job.server == server) & (Job.bfs_layer == bfs_layer)).order_by(
                Job.created_date).first()
            if next_job is not None:
                jobs_to_be_crawled.append(next_job)
            if len(jobs_to_be_crawled) == CRAWL_BATCH_SIZE:
                break
        servers = [job.server for job in jobs_to_be_crawled]
        LOG.info(
            f"# Proceed to crawl {len(jobs_to_be_crawled)} jobs. {servers}")
        LOG.info("#" * 50)
        return jobs_to_be_crawled


class Crawler:
    """Represents a web crawler that retrieves a single page, classifies its relevance, and extracts information."""

    def __init__(self, job: Job):
        """Initialize the Crawler object with a job to crawl.

        Args:
            job (Job): The job representing the URL to be crawled.
        """
        self.job: Job = job

    def harvest_jobs_from_relevant_document(
            self, document: Document) -> list[dict]:
        """Extract relevant jobs from a crawled document.

        Args:
            document (Document): The crawled document.

        Returns:
            list[dict]: A list of job dictionaries representing the relevant URLs found in the document.
        """
        batch = []
        for new_harvested_url in document.relevant_links_list:
            new_harvested_server = utils.get_domain_name_without_subdomain_and_suffix_from_url(
                new_harvested_url)
            new_harvested_domain = utils.get_domain_name_without_subdomain_from_url(
                new_harvested_url)
            job = Job(bfs_layer=self.job.bfs_layer + 1,
                      url=new_harvested_url, server=new_harvested_server,
                      domain=new_harvested_domain)
            batch.append(model_to_dict(job))
        return batch

    def classify_document_relevance(self, document: Document):
        """Classify the relevance of a crawled document.

        Args:
            document (Document): The crawled document to be classified.
        """
        is_body_relevant = utils.do_tokens_contain_tuebingen(
            document.tokens_list)
        is_url_relevant = utils.is_url_and_server_allowed(self.job.url,
                                                          self.job.server)
        is_english = utils.do_text_contain_english_content(document.text)
        if not (is_url_relevant or is_body_relevant):
            LOG.error(
                f"[Layer {self.job.bfs_layer}] Neither document's content nor it's url is not relevant to Tuebingen!: {document.url}")
            document.relevant = False
        elif not is_english:
            LOG.error(
                f"[Layer {self.job.bfs_layer}] Document is not english!: {document.url}")
            document.relevant = False
        else:
            document.relevant = True

    def generate_document_from_html(self, html: str, links: list[str]) -> Document:
        """Generate a Document object from the HTML content of a crawled page.

        Args:
            html (object): Response's text.
            links (list[str]): A list of links harvested from the crawled page.
        Returns:
            Document: The generated Document object.
        """
        messy_text = utils.strip_text_title_and_tags_from_html(html)
        tokens = utilities.preprocess_text_and_tokenize(messy_text)
        text = utils.make_text_human_readable(messy_text)
        harvested_links = links
        title = utils.make_text_human_readable(utils.get_title_from_html(html))
        relevant_links = [
            url for url in harvested_links if utils.is_url_relevant(url)]
        non_relevant_links = [
            url for url in harvested_links if not utils.is_url_relevant(url)]
        return Document(bfs_layer=self.job.bfs_layer,
                        url=self.job.url,
                        server=utils.get_domain_name_without_subdomain_and_suffix_from_url(
                            self.job.url),
                        domain=utils.get_domain_name_without_subdomain_from_url(
                            self.job.url),
                        title=title,
                        text=text,
                        tokens=json.dumps(tokens),
                        all_harvested_links=json.dumps(
                            harvested_links, indent=1),
                        non_relevant_links=json.dumps(
                            non_relevant_links, indent=1),
                        relevant_links=json.dumps(relevant_links, indent=1),
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
                f"[Layer {self.job.bfs_layer}] Error while rendering static website. Response not ok: {response} for URL: {self.job.url}")
        if "html" not in (data_type := response.headers.get("Content-Type")):
            raise Exception(
                f"[Layer {self.job.bfs_layer}] Error while rendering static website. Only accept HTML. Got {data_type} for URL: {self.job.url}")
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
                f"[Layer {self.job.bfs_layer}] Error while rendering dynamic website. Response not ok: {response} for URL: {self.job.url}")
        if "html" not in (data_type := response.headers.get("Content-Type")):
            raise Exception(
                f"[Layer {self.job.bfs_layer}] Error while rendering dynamic website. Only accept HTML. Got {data_type} for URL: {self.job.url}")
        return response

    def crawl_assume_website_is_static(self) -> Document:
        """Try to assume that the website is static and crawl it.

        Returns:
            Document: The crawled Document object.
        """
        response = self.try_to_obtain_static_website_html()
        html = response.text
        links = utils.get_absolute_links(html, self.job.url)
        new_document = self.generate_document_from_html(html, links)
        self.classify_document_relevance(new_document)
        return new_document

    def crawl_assume_website_is_dynamic(self) -> Document:
        """
        Try to assume that the website is dynamic and crawl it.
        :return:
            Document: The crawled Document object.
        """
        response = self.try_to_obtain_static_website_html()
        html = response.text
        links = utils.get_absolute_links(html, self.job.url)
        new_document = self.generate_document_from_html(html, links)
        self.classify_document_relevance(new_document)
        return new_document

    def crawl(self) -> (Document, list[dict]):
        """Perform the crawling process for the given job.

        This procedure tries to crawl the website at least twice.
        One assuming the website is static and one assuming it is dynamic.
        The static crawling is cheaper but less accurate.
        The dynamic crawling is more expensive but more accurate.

        If the static crawling is successful, the dynamic crawling is not performed.
        A static crawling is succesful if the website is relevant to Tuebingen and in english.

        Since we use two different libraries, this code is a bit messy.

        Returns:
            Tuple[Document, list[dict]]: A tuple containing the crawled Document and a list of new job dictionaries.
        """
        if utils.is_job_relevant(self.job):
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
                    return new_document, self.harvest_jobs_from_relevant_document(
                        new_document)
                # Document is not relevant. Do not queue its children.
                return new_document, []
        else:
            LOG.info(
                f"[Layer {self.job.bfs_layer}] Job {self.job.url} is not relevant.")
        return None, []  # Document could not be retrieved.


def main():
    """The main function that initiates the crawling process."""
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("-b", "--bfs_layer", type=int,
                        help="The BFS layer to crawl. If not specified, crawl the next smallest BFS layer.")
    parser.add_argument("-n", "--number", type=int, default=math.inf,
                        help="How many documents should be crawled")
    args = parser.parse_args()

    document_retrieved = 0
    LOG.info(f"Proceed to retrieve {args.number} jobs.")
    while len(jobs := PriorityQueue(
            args.bfs_layer).get_jobs_from_database_to_crawl()) > 0 and document_retrieved < args.number:
        with multiprocessing.Manager() as manager:
            shared_results = manager.list([(None, []) for _ in jobs])
            time.sleep(
                random.uniform(
                    *CRAWL_RANDOM_SLEEP_INTERVAL))  # Random delay

            def process_job(j_idx, j):
                shared_results[j_idx] = Crawler(j).crawl()

            processes = []
            for i, job in enumerate(jobs):
                processes.append(
                    multiprocessing.Process(
                        target=process_job, args=(
                            i, job)))
                processes[-1].start()

            for process in processes:
                process.join()

            for job, (new_document, new_jobs) in zip(jobs, shared_results):
                with DATABASE.atomic() as transaction:
                    try:
                        if new_document is not None:
                            new_document.save()
                            if new_document.relevant:
                                Job.insert_many(
                                    new_jobs).on_conflict_ignore().execute()
                            Job.update(
                                done=True, success=True).where(
                                Job.id == job.id).execute()
                        else:
                            Job.update(
                                done=True, success=False).where(
                                Job.id == job.id).execute()
                    except peewee.IntegrityError as error:
                        LOG.error(
                            f"[Layer {job.bfs_layer}] Error saving document {new_document.url}: {error}")
                        transaction.rollback()
                document_retrieved += 1


if __name__ == '__main__':
    main()
