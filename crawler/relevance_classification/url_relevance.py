"""
This module contains functions to check if a URL is relevant for the crawler.
"""
import os
import json

from crawler import utils
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

CRAWL_EXCLUDED_EXTENSIONS = set(json.loads(
    os.getenv("CRAWL_EXCLUDED_EXTENSIONS")))
CRAWL_BLACK_LIST = set(json.loads(os.getenv("CRAWL_BLACK_LIST")))


def get_url_extension(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename, file_extension = os.path.splitext(path)
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
    if is_url_media_link(url):
        return 0

    if utils.url.get_server_name_from_url(url) in CRAWL_BLACK_LIST:
        return 0

    count = 0
    if "bingen" in url:
        count += 1
    if "/en/" in url:
        count += 1
    if "en." in url:
        count += 1
    return count


def is_url_relevant(url: str) -> bool:
    """
    Check if a URL is relevant for the crawler.
    Args:
        url: The URL to check.
    Returns: True if the URL is relevant, False otherwise.
    """
    return get_url_priority(url) > 0
