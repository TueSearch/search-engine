"""
This module contains utility functions for URL parsing.
"""
import functools
import json
import os
from urllib.parse import urljoin, urlparse, urlunparse

import spacy
import tldextract
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from url_normalize import url_normalize

from crawler import utils
from crawler.sql_models.document import Document
from crawler.utils import text
from crawler.utils.text import make_text_human_readable
from crawler.ml_models.url_relevance_predictor import ml_predict_url_relevance

load_dotenv()

# Credit: https://stackoverflow.com/a/68030892
NLP = spacy.blank("en")
NLP.tokenizer.url_match = None
infixes = NLP.Defaults.infixes + [r'\.']
infix_regex = spacy.util.compile_infix_regex(infixes)
NLP.tokenizer.infix_finditer = infix_regex.finditer

CRAWL_EXCLUDED_EXTENSIONS = utils.io.read_json_file("data/excluded_extensions.json")
CRAWL_SURROUNDING_TEXT_LENGTH = int(os.getenv('CRAWL_SURROUNDING_TEXT_LENGTH'))
TUEBINGEN_WRITING_STYLES = utils.io.read_json_file("data/tuebingen_writing_styles.json")


@functools.lru_cache
def get_blocked_patterns():
    with open("data/blocked_patterns.json", "r") as f:
        return json.loads(f.read())


class URL:
    def __init__(self, url: str,
                 parent: Document = None,
                 anchor_text: str = "",
                 surrounding_text: str = "",
                 title_text: str = ""):
        url = url_normalize(url)
        parsed_url = urlparse(url)
        parsed_url = parsed_url._replace(fragment='')
        self.url = urlunparse(parsed_url)
        self.anchor_text = utils.text.make_text_human_readable(anchor_text)
        self.surrounding_text = utils.text.make_text_human_readable(surrounding_text)
        self.title_text = utils.text.make_text_human_readable(title_text)
        self.parent = parent

    def __eq__(self, other):
        return self.url == other.url

    def __neq__(self, other):
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    def __str__(self):
        return f"URL[url={self.url}, anchor_text={self.anchor_text}]"

    def __repr__(self):
        return str(self)

    @staticmethod
    def get_links(parent_document: Document, parent_url: str) -> list['URL']:
        """
        Extracts all absolute links from HTML content.

        Args:
            html (str): The HTML content.
            url (str): The URL used to resolve the absolute links.

        Returns:
            list: A list of absolute links extracted from the HTML.
        """

        soup = BeautifulSoup(parent_document.html, 'html.parser')
        body_text = make_text_human_readable(soup.body.get_text(separator=" "))

        def get_surrounding_text(anchor) -> str:
            # Search for the index of the anchor text in the body text
            index = body_text.find(anchor)
            if index != -1:
                # Extract the substring of CRAWL_SURROUNDING_TEXT_LENGTH words before and after the anchor text
                return body_text[max(0, index - CRAWL_SURROUNDING_TEXT_LENGTH):index + len(
                    anchor) + CRAWL_SURROUNDING_TEXT_LENGTH]
            return ""

        links = []

        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                absolute_url = urljoin(parent_url, href)
                anchor_text = link.get_text()
                links.append(
                    URL(url=absolute_url,
                        anchor_text=anchor_text,
                        surrounding_text=get_surrounding_text(anchor_text),
                        title_text=link.get('title', ''),
                        parent=parent_document))
        return links

    @functools.cached_property
    def server_name(self):
        """
        Extracts the server name of a URL.
        """    
        extracted = tldextract.extract(self.url)
        out = extracted.subdomain + '.' + extracted.domain + '.' + extracted.suffix
        out_tokens = out.split(".")
        if out_tokens[0] == "www":
            return ".".join(out_tokens[1:])
        return out

    @functools.cached_property
    def tld(self):
        """
        Extracts the top-level domain of a URL.
        """
        return tldextract.extract(self.url).suffix

    @functools.cached_property
    def url_tokens(self) -> list[str]:
        """
        Tokenizes a URL.

        Args:
            url (str): Input URL.

        Returns:
            list[str]: List of tokens.
        """
        tokens = list(NLP(self.url))
        tokens = [token.text for token in tokens if not token.is_punct]
        return tokens

    @functools.cached_property
    def anchor_text_tokens(self) -> list[str]:
        """
        Tokenizes a URL.

        Args:
            url (str): Input URL.

        Returns:
            list[str]: List of tokens.
        """
        return text.advanced_tokenize_with_pos(self.anchor_text)

    @functools.cached_property
    def surrounding_text_tokens(self) -> list[str]:
        """
        Tokenizes a URL.

        Args:
            url (str): Input URL.

        Returns:
            list[str]: List of tokens.
        """
        return text.advanced_tokenize_with_pos(self.surrounding_text)

    @functools.cached_property
    def title_text_tokens(self) -> list[str]:
        """
        Tokenizes a URL.

        Args:
            url (str): Input URL.

        Returns:
            list[str]: List of tokens.
        """
        return text.advanced_tokenize_with_pos(self.title_text)

    @functools.cached_property
    def extension(self):
        """
        Extracts the extension of a URL.
        """
        parsed_url = urlparse(self.url)
        path = parsed_url.path
        _, file_extension = os.path.splitext(path)
        return file_extension

    @functools.cached_property
    def is_properly_a_html_site(self):
        """
        Check if a URL is a "normal" text URL.

        Returns:
            bool: True if the URL is a "normal" text URL, False otherwise.
        """
        ext = self.extension
        for media_extension in CRAWL_EXCLUDED_EXTENSIONS:
            if media_extension in ext:
                return False
        return True

    @functools.cached_property
    def is_a_real_hyper_link(self) -> bool:
        """
        Check if a text is a URL.
        """

        def test1():
            try:
                result = urlparse(self.url)
                return all([result.scheme, result.netloc])
            # pylint: disable=broad-except
            except:
                return False

        def test2():
            result = validators.url(self.url)
            if isinstance(result, validators.ValidationFailure):
                return False
            return result

        return test1() and test2()

    @functools.cached_property
    def contains_blocked_patterns(self) -> bool:
        """
        Check if the URL contains blocked patterns.
        """
        for pattern in get_blocked_patterns():
            if pattern in self.url:
                return True
        return False

    @functools.cached_property
    def priority(self) -> int:
        """
        Returns the priority of the URL.
        """
        if self.contains_blocked_patterns:
            return -1

        if not self.is_properly_a_html_site:
            return -1

        if not self.is_a_real_hyper_link:
            return -1

        total_points = 0

        if ml_predict_url_relevance(self) == 1:
            total_points += 30

        return total_points

    @functools.cached_property
    def is_relevant(self) -> bool:
        """
        Returns true if the URL is relevant.
        """
        return self.priority >= 0
