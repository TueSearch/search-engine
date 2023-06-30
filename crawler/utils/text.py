"""
This module contains functions to process text.
"""
import html
import os
import re

import spacy
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langdetect import detect_langs
from unidecode import unidecode
from spacy.tokens.token import Token

load_dotenv()

NLP = spacy.load(os.getenv("SPACY_MODEL"))
NLP.add_pipe("emoji", first=True)
REMOVE_LONG_WORD_THRESHOLD = int(os.getenv("REMOVE_LONG_WORD_THRESHOLD"))
CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD = float(os.getenv("CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD"))
CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD = float(os.getenv("CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD"))


def remove_hyperlinks_from_text(text: str) -> str:
    """
    Removes hyperlinks from a given text.

    Args:
        text (str): Input text.

    Returns:
        str: Text with hyperlinks removed.
    """
    # Regular expression pattern to match hyperlinks
    pattern = re.compile(r'https?://\S+|www\.\S+')
    return re.sub(pattern, '', text)


def spacy_tokenize(text: str) -> list[Token]:
    """
    Tokenizes the given text.
    Args:
        text: input text

    Returns: list of strings

    """
    text = text.lower()

    text = html.unescape(text)

    text = remove_hyperlinks_from_text(text)

    text = text.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "s").replace("ã¼", "u").replace(
        "Ã¼", "u")
    # print(("#" * 20) + f"Remove german umlaute {tokens}", file=sys.stderr)

    tokens = list(NLP(text))
    # print(("#" * 20) + f"Tokenize and lower case {tokens}", file=sys.stderr)

    tokens = [token for token in tokens if not token._.is_emoji]
    # print(("#" * 20) + f"Lower and strip {tokens}", file=sys.stderr)

    tokens = [token for token in tokens if not token.is_stop]
    # print(("#" * 20) + f"Remove EN stop tokens {tokens}", file=sys.stderr)

    tokens = [token for token in tokens if token.is_ascii]
    # print(("#" * 20) + f"Remove non-ascii {tokens}", file=sys.stderr)

    tokens = [token for token in tokens if not token.is_punct]
    # print(("#" * 20) + f"Remove punctuation {tokens}", file=sys.stderr)

    tokens = [token for token in tokens if len(token.text) < REMOVE_LONG_WORD_THRESHOLD]
    # print(("#" * 20) + f"Remove very long tokens {tokens}", file=sys.stderr)

    tokens = [token for token in tokens if not token.is_digit]

    tokens = [token for token in tokens if len(token.text) > 1]

    return tokens


def advanced_tokenize_with_pos(text: str) -> list[str]:
    """
    Tokenizes the given text.
    Args:
        text: input text

    Returns: list of strings

    """
    tokens = spacy_tokenize(text)

    return [f"{t.lemma_}_{t.pos_}" for t in tokens]


def tokenize_get_lang(text: str) -> list[str]:
    """
    Tokenizes the given text.
    Args:
        text: input text

    Returns: list of strings

    """
    tokens = spacy_tokenize(text)

    return [t.lang_ for t in tokens]


def do_text_contain_english_content(text: str) -> bool:
    """
    Determines if the given text contains English content based on language detection probabilities.

    Args:
        text (str): The text to analyze.

    Returns:
        bool: True if the text contains English content, False otherwise.
    """

    try:
        # Attempt to detect the languages present in the text
        langs = detect_langs(text)

        # Iterate over the detected languages
        for lang in langs:
            # Check if the language is English
            if lang.lang == "en":
                # Check the probability of English content based on thresholds
                if len(langs) > 1:
                    # For multiple detected languages, compare probability
                    # against a multi_threshold
                    return lang.prob >= (
                            1 / len(langs) + CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD)
                # For single detected language, compare probability against
                # a single_threshold
                return lang.prob >= CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD

        # If English language is not detected, return False
        return False
    except Exception as _:
        # If an exception occurs during language detection, return False
        return False


def generate_text_document_from_html(html_content: str) -> 'Document':
    """
    Extracts plain text from HTML content.

    Args:
        html_content (str): HTML content.

    Returns:
        (str, str): Title and body extracted from HTML, if any. Default empty strings.
    """
    from crawler.sql_models.document import Document

    soup = BeautifulSoup(html_content, 'html.parser')

    document = Document()

    document.body = make_text_human_readable(soup.body.get_text(separator=" "))
    document.body_tokens = advanced_tokenize_with_pos(document.body)

    document.title = make_text_human_readable(soup.title.string if soup.title else "")
    document.title_tokens = advanced_tokenize_with_pos(document.title)

    # Add meta information to the document
    meta_tags = soup.find_all('meta')
    for meta_tag in meta_tags:
        if 'name' in meta_tag.attrs and 'content' in meta_tag.attrs:
            name = meta_tag.attrs['name']
            content = meta_tag.attrs['content']
            if name == 'description':
                document.meta_description = make_text_human_readable(content)
                document.meta_description_tokens = advanced_tokenize_with_pos(document.meta_description)
            elif name == 'keywords':
                document.meta_keywords = make_text_human_readable(content)
                document.meta_keywords_tokens = advanced_tokenize_with_pos(document.meta_keywords)
            elif name == 'author':
                document.meta_author = make_text_human_readable(content)
                document.meta_author_tokens = advanced_tokenize_with_pos(document.meta_author)

    # Set h1, h2, h3, h4, h5, h6 fields
    h1_tags = soup.find_all('h1')
    document.h1 = make_text_human_readable(' '.join([h1.get_text().strip() for h1 in h1_tags]))
    document.h1_tokens = advanced_tokenize_with_pos(document.h1)

    h2_tags = soup.find_all('h2')
    document.h2 = make_text_human_readable(' '.join([h2.get_text().strip() for h2 in h2_tags]))
    document.h2_tokens = advanced_tokenize_with_pos(document.h2)

    h3_tags = soup.find_all('h3')
    document.h3 = make_text_human_readable(' '.join([h3.get_text().strip() for h3 in h3_tags]))
    document.h3_tokens = advanced_tokenize_with_pos(document.h3)

    h4_tags = soup.find_all('h4')
    document.h4 = make_text_human_readable(' '.join([h4.get_text().strip() for h4 in h4_tags]))
    document.h4_tokens = advanced_tokenize_with_pos(document.h4)

    h5_tags = soup.find_all('h5')
    document.h5 = make_text_human_readable(' '.join([h5.get_text().strip() for h5 in h5_tags]))
    document.h5_tokens = advanced_tokenize_with_pos(document.h5)

    h6_tags = soup.find_all('h6')
    document.h6 = make_text_human_readable(' '.join([h6.get_text().strip() for h6 in h6_tags]))
    document.h6_tokens = advanced_tokenize_with_pos(document.h6)

    return document


def make_text_human_readable(text):
    """
    Cleans the given text by removing newlines and ensuring there is only one whitespace between each token.

    Args:
        text (str): The input text to be cleaned.

    Returns:
        str: The cleaned text with newlines removed and single whitespaces between tokens.
    """
    # Remove newlines
    cleaned_text = text.replace('\n', ' ')

    # Replace multiple whitespaces with a single whitespace
    cleaned_text = re.sub('\\s+', ' ', cleaned_text)

    # Remove leading and trailing whitespaces
    cleaned_text = cleaned_text.strip()

    return unidecode(cleaned_text)
