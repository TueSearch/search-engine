"""
This module contains functions to process text.
"""
import html
import re

from bs4 import BeautifulSoup
from langdetect import detect_langs
from unidecode import unidecode
import spacy
import os
from dotenv import load_dotenv

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


def tokenize(text: str) -> list[str]:
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

    return [f"{t.lemma_}_{t.pos_}" for t in tokens]

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


def get_title_and_body_from_html(html_content: str) -> (str, str):
    """
    Extracts plain text from HTML content.

    Args:
        html_content (str): HTML content.

    Returns:
        (str, str): Title and body extracted from HTML, if any. Default empty strings.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.title.string if soup.title else ""
    body = soup.get_text(separator=" ")
    title = make_text_human_readable(title)
    body = make_text_human_readable(body)
    title = unidecode(title)
    body = unidecode(body)
    return title, body


def extract_content_from_tag(html_content: str, tag_name: str) -> str:
    """
    Extracts the content from a specified HTML tag.

    Args:
        html_content (str): HTML content.
        tag_name (str): Name of the tag to extract content from.

    Returns:
        str: Content extracted from the specified tag.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    tag = soup.find(tag_name)
    if tag:
        ret = tag.text
        if "content" in tag:
            ret += " " + tag["content"]
        return ret
    # Handle the case when the tag is not found
    return ""


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

    return cleaned_text
