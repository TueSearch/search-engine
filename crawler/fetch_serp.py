"""
crawler/fetch_serp.py - SERP Fetching

This module is responsible for fetching search engine results page (SERP) data using the SERP API.
It defines functions to query the API, crawl SERP data for different keywords and topics,
and provides a class for crawling search results using different writing styles of 'Tübingen'.
"""
import json
import os

from dotenv import load_dotenv
import requests
from crawler import utils

load_dotenv()

# Load environment variables
# List of topics for SERP queries
SERP_TOPICS = json.loads(os.getenv("SERP_TOPICS"))
SERP_FILE = os.getenv("SERP_FILE")  # Output file to store the SERP results
LOG = utils.get_logger(__file__)  # Logger for logging messages
SERP_API_KEY = os.getenv("SERP_API_KEY")  # API key for the SERP API
# Number of results per page
SERP_GOOGLE_PAGE_SIZE = int(os.getenv("SERP_GOOGLE_PAGE_SIZE"))
# Page number of Google search results
SERP_GOOGLE_PAGE = int(os.getenv("SERP_GOOGLE_PAGE"))


def query_serp_api(url, query):
    """
    Query the SERP API with a given URL and query.

    Args:
        url (str): URL of the SERP API endpoint
        query (str): Query string

    Returns:
        dict: JSON response from the SERP API
    """
    headers = {
        'X-API-KEY': SERP_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "autocorrect": False,
        "gl": "gb",
        "page": SERP_GOOGLE_PAGE,
        "num": SERP_GOOGLE_PAGE_SIZE,
        "q": query
    })
    return requests.request("POST", url, headers=headers, data=payload, timeout=5).json()


def query_serp_api_search(query):
    """
    Query the SERP API for search results.

    Args:
        query (str): Query string

    Returns:
        dict: JSON response from the SERP API
    """
    return query_serp_api("https://google.serper.dev/search", query)


def query_serp_api_news(query):
    """
    Query the SERP API for news results.

    Args:
        query (str): Query string

    Returns:
        dict: JSON response from the SERP API
    """
    return query_serp_api("https://google.serper.dev/news", query)


def crawl_only_key_word_tuebingen(tuebingen_writing_style: str) -> dict:
    """
    Crawl the SERP API for search results using only the keyword 'Tübingen'.

    Args:
        tuebingen_writing_style (str): Writing style of 'Tübingen' keyword

    Returns:
        dict: JSON response from the SERP API
    """
    return query_serp_api_search(tuebingen_writing_style)


def crawl_key_word_tuebingen_plus_topic(
        topic: str, tuebingen_writing_style: str) -> dict:
    """
    Crawl the SERP API for search results using the keyword 'Tübingen' plus a given topic.

    Args:
        topic (str): Topic to include in the query
        tuebingen_writing_style (str): Writing style of 'Tübingen' keyword

    Returns:
        dict: JSON response from the SERP API
    """
    return query_serp_api_search(f"{tuebingen_writing_style} {topic}")


def crawl_tuebingen_news(tuebingen_writing_style: str) -> dict:
    """
    Crawl the SERP API for news results using the keyword 'Tübingen'.

    Args:
        tuebingen_writing_style (str): Writing style of 'Tübingen' keyword

    Returns:
        dict: JSON response from the SERP API
    """
    return query_serp_api_news(tuebingen_writing_style)


class SERPCrawler:
    """
    Class for crawling search results using different writing styles of 'Tübingen'.
    """

    def __init__(self):
        self.results: dict[str, dict] = self.read_serp_results()

    @staticmethod
    def read_serp_results() -> dict[str, dict]:
        """
        Read the existing SERP results from a JSON file.

        Returns:
            dict: Dictionary containing the SERP results
        """
        try:
            return utils.io.read_json_file(SERP_FILE)
        except Exception as error:
            LOG.error(
                f"Error reading current SERP files. {str(error)}. Use empty initial SERP and start download new SERP.")
            return {}

    def crawl_with_writing_style(self, tuebingen_writing_style: str):
        """
        Crawl the SERP API for search and news results using a given writing style of 'Tübingen'.

        Args:
            tuebingen_writing_style (str): Writing style of 'Tübingen' keyword
        """
        for topic in SERP_TOPICS:
            key = f"{tuebingen_writing_style}_{SERP_GOOGLE_PAGE}_{topic}"
            if key not in self.results:
                self.results[key] = crawl_key_word_tuebingen_plus_topic(
                    topic, tuebingen_writing_style)
                LOG.info(
                    f"Downloaded {tuebingen_writing_style} {topic} {SERP_GOOGLE_PAGE}.")
            else:
                LOG.info(
                    f"Skipped {tuebingen_writing_style} {topic} {SERP_GOOGLE_PAGE}")

        key = f"{tuebingen_writing_style}_{SERP_GOOGLE_PAGE}"
        if key not in self.results:
            self.results[key] = crawl_only_key_word_tuebingen(
                tuebingen_writing_style)
            LOG.info(
                f"Downloaded {tuebingen_writing_style} {SERP_GOOGLE_PAGE}.")
        else:
            LOG.info(f"Skipped {tuebingen_writing_style} {SERP_GOOGLE_PAGE}")

        key = f"{tuebingen_writing_style}_{SERP_GOOGLE_PAGE}_news"
        if key not in self.results:
            self.results[key] = crawl_tuebingen_news(tuebingen_writing_style)
            LOG.info(f"Downloaded {tuebingen_writing_style} news.")
        else:
            LOG.info(f"Skipped {tuebingen_writing_style} news")


def main():
    """
    Main function to start the SERP crawling process.
    """
    serp_crawler = SERPCrawler()
    try:
        LOG.info("Start crawling Tübingen")
        serp_crawler.crawl_with_writing_style("Tübingen")
        LOG.info("Start crawling Tuebingen")
        serp_crawler.crawl_with_writing_style("Tuebingen")
        LOG.info("Start crawling Tubingen")
        serp_crawler.crawl_with_writing_style("Tubingen")
    except KeyboardInterrupt as error:
        LOG.info(f"Interrupted. Store downloaded data and exit: {str(error)}")
    except Exception as error:
        LOG.info(
            f"Unknown exception {str(error)}. Store downloaded data and exit!")
    utils.io.write_json_file(serp_crawler.results, SERP_FILE)


def reset():
    """
    Reset function to delete the SERP output file.
    """
    utils.io.delete_file(SERP_FILE)


if __name__ == '__main__':
    main()
