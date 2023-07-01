"""
This module contains utility functions for URL parsing.
"""
import json
import os
from urllib.parse import urljoin, urlparse, urlunparse
import functools
import spacy
import tldextract
import validators
from bs4 import BeautifulSoup
from url_normalize import url_normalize
from dotenv import load_dotenv

from crawler import utils
from crawler.relevance_classification.document_relevance import get_document_approximated_relevance_score_for
from crawler.sql_models.document import Document
from crawler.utils.text import tokenize_get_lang, make_text_human_readable

from crawler.utils import text

load_dotenv()

# Credit: https://stackoverflow.com/a/68030892
NLP = spacy.blank("en")
NLP.tokenizer.url_match = None
infixes = NLP.Defaults.infixes + [r'\.']
infix_regex = spacy.util.compile_infix_regex(infixes)
NLP.tokenizer.infix_finditer = infix_regex.finditer

CRAWL_EXCLUDED_EXTENSIONS = set(json.loads(
    os.getenv("CRAWL_EXCLUDED_EXTENSIONS")))
CRAWL_BLACK_LIST = set(json.loads(os.getenv("CRAWL_BLACK_LIST")))
QUEUE_MANUAL_SEEDS = json.loads(os.getenv('QUEUE_MANUAL_SEEDS'))
CRAWL_PRIORITY_LIST = json.loads(os.getenv('CRAWL_PRIORITY_LIST'))
TUEBINGEN_WRITING_STYLES = json.loads(os.getenv('TUEBINGEN_WRITING_STYLES'))


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
                # Extract the substring of 20 words before and after the anchor text
                return body_text[max(0, index - 20):index + len(anchor) + 20]
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
        return tldextract.extract(self.url).domain

    @functools.cached_property
    def tld(self):
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
            except:
                return False

        def test2():
            result = validators.url(self.url)
            if isinstance(result, validators.ValidationFailure):
                return False
            return result

        return test1() and test2()

    @functools.cached_property
    def is_on_server_black_list(self) -> bool:
        return self.server_name in CRAWL_BLACK_LIST

    @functools.cached_property
    def count_tuebingen_in_url(self) -> int:
        count = 0
        for token in self.url_tokens:
            for tueb in TUEBINGEN_WRITING_STYLES:
                if tueb in token:
                    count += 1
        return count

    @functools.cached_property
    def count_bingen_in_url(self) -> int:
        count = 0
        for token in self.url_tokens:
            if "bingen" in token:
                count += 1
        return count

    @functools.cached_property
    def count_en_in_url(self) -> int:
        count = 0
        for token in self.url_tokens:
            if "en" in token or "/en" in token or "/en/" in token or ".en" in token or ".en/" in token or ".en." in token:
                count += 1
        return count

    @functools.cached_property
    def get_priority_list_bonus(self) -> int:
        count = 0
        for priority_url in CRAWL_PRIORITY_LIST:
            if priority_url in self.url:
                count += 20
        return count

    @functools.cached_property
    def get_initial_queue_list_bonus(self) -> int:
        count = 0
        for priority_url in QUEUE_MANUAL_SEEDS:
            if priority_url in self.url:
                count += 100000
        return count

    @functools.cached_property
    def get_international_suffix_bonus(self) -> int:
        count = 0
        if "com" in self.tld:
            count += 1
        return count

    @functools.cached_property
    def count_tuebingen_in_anchor_text(self) -> int:
        count = 0
        for token in self.anchor_text_tokens:
            for tueb in TUEBINGEN_WRITING_STYLES:
                if tueb in token:
                    count += 1
        return count

    @functools.cached_property
    def count_bingen_in_anchor_text(self) -> int:
        count = 0
        for token_lang in tokenize_get_lang(self.anchor_text):
            if "en" in token_lang:
                count += 1
        return count

    @functools.cached_property
    def count_tuebingen_in_surrounding_text(self) -> int:
        count = 0
        for token in self.surrounding_text_tokens:
            for tueb in TUEBINGEN_WRITING_STYLES:
                if tueb in token:
                    count += 1
        return count

    @functools.cached_property
    def count_bingen_in_surrounding_text(self) -> int:
        count = 0
        for token_lang in tokenize_get_lang(self.surrounding_text):
            if "en" in token_lang:
                count += 1
        return count

    @functools.cached_property
    def count_tuebingen_in_title_text(self) -> int:
        count = 0
        for token in self.title_text_tokens:
            for tueb in TUEBINGEN_WRITING_STYLES:
                if tueb in token:
                    count += 1
        return count

    @functools.cached_property
    def count_bingen_in_title_text(self) -> int:
        count = 0
        for token_lang in tokenize_get_lang(self.title_text):
            if "en" in token_lang:
                count += 1
        return count

    @functools.cached_property
    def count_english_(self) -> int:
        count = 0
        for token in self.url_tokens:
            if "en" in token or "/en" in token or "/en/" in token or ".en" in token or ".en/" in token or ".en." in token:
                count += 20
        return count

    @functools.cached_property
    def priority(self) -> int:
        if not self.is_properly_a_html_site:
            return -1

        if not self.is_a_real_hyper_link:
            return -1

        if self.is_on_server_black_list:
            return -1

        total_points = 0
        total_points += 5 * self.count_tuebingen_in_url
        total_points += 1 * self.count_bingen_in_url
        total_points += 20 * self.count_en_in_url
        total_points += self.get_priority_list_bonus
        total_points += self.get_initial_queue_list_bonus
        total_points += self.get_international_suffix_bonus
        total_points += 10 * self.count_tuebingen_in_anchor_text
        total_points += 5 * self.count_bingen_in_anchor_text
        total_points += 10 * self.count_tuebingen_in_title_text
        total_points += 5 * self.count_bingen_in_surrounding_text
        total_points += 0 if self.parent is None else get_document_approximated_relevance_score_for(self.parent)
        return total_points

    @functools.cached_property
    def is_relevant(self) -> bool:
        return self.priority > 0
