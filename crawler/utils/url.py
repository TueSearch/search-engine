"""
This module contains utility functions for URL parsing.
"""
import json
from urllib.parse import urljoin, urlparse, urlunparse
import os

import tldextract
from bs4 import BeautifulSoup
from url_normalize import url_normalize
from dotenv import load_dotenv

load_dotenv()

CRAWL_EXCLUDED_EXTENSIONS = set(json.loads(
    os.getenv("CRAWL_EXCLUDED_EXTENSIONS")))
CRAWL_BLACK_LIST = set(json.loads(os.getenv("CRAWL_BLACK_LIST")))
INVERTED_INDEX_TUEBINGEN_WRITING_STYLES = set(json.loads(
    os.getenv("INVERTED_INDEX_TUEBINGEN_WRITING_STYLES")))
CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD = float(
    os.getenv("CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD"))
CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD = float(
    os.getenv("CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD"))


def get_server_name_from_url(url: str):
    """
    Extracts the domain name without subdomain and suffix from a given URL.

    Args:
        url (str): Input URL.

    Returns:
        str: Extracted domain name without subdomain and suffix.
    """
    return tldextract.extract(url).domain


def get_absolute_links(html, url):
    """
    Extracts all absolute links from HTML content.

    Args:
        html (str): The HTML content.
        url (str): The URL used to resolve the absolute links.

    Returns:
        list: A list of absolute links extracted from the HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    absolute_links = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            absolute_url = urljoin(url, href)
            absolute_links.append(absolute_url)

    return absolute_links


def get_all_urls_from_html(html: str, current_url: str):
    """
    Extracts all URLs from HTML content.

    Args:
        html (str): HTML content.
        current_url (str): URL of the current page.

    Returns:
        list[str]: List of extracted URLs.
    """
    soup = BeautifulSoup(html, 'html.parser')
    urls = set()

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            url = urljoin(current_url, href)  # Resolve relative URLs
            try:
                url = normalize_url(url)
                urls.add(url)
            except Exception as _:
                pass
    return list(urls)


def normalize_url(url: str) -> str:
    """
    Normalizes a URL by removing unnecessary components and applying standardization rules.

    Args:
        url (str): Input URL.

    Returns:
        str: Normalized URL.
    """
    url = url_normalize(url)
    parsed_url = urlparse(url)
    parsed_url = parsed_url._replace(fragment='')
    return urlunparse(parsed_url)
