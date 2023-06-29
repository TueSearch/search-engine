"""
This module contains functions to check if a URL is relevant for the crawler.
"""
import json
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
import validators

from crawler import utils
from tldextract import extract

load_dotenv()

CRAWL_EXCLUDED_EXTENSIONS = set(json.loads(
    os.getenv("CRAWL_EXCLUDED_EXTENSIONS")))
CRAWL_BLACK_LIST = set(json.loads(os.getenv("CRAWL_BLACK_LIST")))
QUEUE_MANUAL_SEEDS = json.loads(os.getenv('QUEUE_MANUAL_SEEDS'))


def get_url_extension(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    _, file_extension = os.path.splitext(path)
    return file_extension


def is_url_media_link(url):
    """
    Check if a URL is a "normal" text URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a "normal" text URL, False otherwise.
    """
    ext = get_url_extension(url)
    for exclued_extension in CRAWL_EXCLUDED_EXTENSIONS:
        if exclued_extension in ext:
            return True
    return False


def get_url_priority(url: str) -> int:
    """
    Get the priority of a URL.
    Args:
        url: The URL to get the priority of.

    Returns: The priority of the URL. The higher the number, the higher the priority.

    """
    if not is_url(url):
        return -1

    if is_url_media_link(url):
        return -1

    if utils.url.get_server_name_from_url(url) in CRAWL_BLACK_LIST:
        return -1

    count = 1
    if "bingen" in url:
        count += 2
    if "/en/" in url:
        count += 1
    if "en." in url:
        count += 1
    if url in QUEUE_MANUAL_SEEDS:
        count += 100
    if extract(url).suffix == "com":
        count += 1
    return count


def is_url(text: str) -> bool:
    """
    Check if a text is a URL.
    """

    def test1():
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False

    def test2():
        result = validators.url(text)
        if isinstance(result, validators.ValidationFailure):
            return False
        return result

    return test1() and test2()


def is_url_relevant(url: str) -> bool:
    """
    Check if a URL is relevant for the crawler.
    Args:
        url: The URL to check.
    Returns: True if the URL is relevant, False otherwise.
    """
    return get_url_priority(url) > 0

