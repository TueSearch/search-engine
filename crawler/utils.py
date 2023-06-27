"""
crawler/utils
~~~~~~~~~

This module provides utility functions for the MSE project.

"""
import functools
import json
import logging
import os
import re
import shutil
import sys
import unicodedata
from logging.handlers import RotatingFileHandler
from urllib.parse import urljoin, urlparse, urlunparse
from pathlib import Path
import html

import _pickle as pickle
import spacy
import tldextract
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langdetect import detect, detect_langs
from nltk.corpus import stopwords
from url_normalize import url_normalize

# Load environment variables and other stuff
load_dotenv()

# Set up global variables
NLP_TOKENIZER = spacy.load(os.getenv("SPACY_TOKENIZER_MODEL"))
NLP_LEMMATIZER = spacy.load(os.getenv("SPACY_ENGLISH_LEMMATIZATION_MODEL"))
ENGLISH_STOP_WORDS = set(stopwords.words('english'))
CRAWL_EXCLUDED_EXTENSIONS = set(json.loads(
    os.getenv("CRAWL_EXCLUDED_EXTENSIONS")))
CRAWL_BLACK_LIST = set(json.loads(os.getenv("CRAWL_BLACK_LIST")))
INVERTED_INDEX_TUEBINGEN_WRITING_STYLES = set(json.loads(
    os.getenv("INVERTED_INDEX_TUEBINGEN_WRITING_STYLES")))
CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD = float(
    os.getenv("CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD"))
CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD = float(
    os.getenv("CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD"))


@functools.cache
def punctuation_characters():
    """
    Retrieves a set of garbage characters, used as punctuation.

    Returns:
        set: A set of garbage characters, used as punctuation.
    """
    garbages_categories = ["P", "S", "Z"]
    return set(
        [c for c in [chr(i) for i in range(65536)] if unicodedata.category(c)[0] in garbages_categories] + ["--"])


def read_json_file(path: str) -> json:
    """
    Reads a JSON file and returns the parsed JSON object.

    Args:
        path (str): Path to the JSON file.

    Returns:
        json: Parsed JSON object.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(json_object: json, path: str):
    """
    Writes a JSON object to a file in JSON format.

    Args:
        json_object (json): JSON object to be written to the file.
        path (str): Path to the output JSON file.
    """
    create_parent_directory_if_not_exist(path)
    with open(path, "w", encoding="utf-8") as file:
        return json.dump(json_object, file)


def read_pickle_file(path: str) -> json:
    """
    Reads a pickled object from a file and returns it.

    Args:
        path (str): Path to the pickled file.

    Returns:
        json: Pickled object.
    """
    with open(path, "rb") as file:
        return pickle.load(file)


def write_pickle_file(json_object: json, path: str):
    """
    Writes a Python object to a file in pickled format.

    Args:
        json_object (json): Python object to be pickled and written to the file.
        path (str): Path to the output pickled file.
    """
    create_parent_directory_if_not_exist(path)
    with open(path, "wb") as file:
        return pickle.dump(json_object, file)


def create_parent_directory_if_not_exist(path: str) -> str:
    """
    Creates the parent directory for a given file path if it does not exist.

    Args:
        path (str): Path to the file.

    Returns:
        str: The input path.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return path


def create_directory_if_not_exists(path: str):
    """
    Creates a directory if it does not exist.

    Args:
        path (str): Path to the directory.

    Returns:
        str: The input path.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def delete_files_in_directory(directory: str):
    """
    Deletes all files in a directory.

    Args:
        directory (str): Path to the directory.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")


def delete_subdirectories_in_directory(directory: str):
    """
    Deletes all subdirectories in a directory.

    Args:
        directory (str): Path to the directory.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                shutil.rmtree(file_path)
                print(f"Deleted directory: {file_path}")


def delete_file(file: str):
    """
    Deletes a file.

    Args:
        file (str): Path to the file.
    """
    if os.path.isfile(file):
        os.remove(file)
        print(f"Deleted file: {file}")


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


def stem_words_of_tokens(tokens: list) -> list:
    """
    Stems the English words of a list of tokens.

    Args:
        tokens (list): List of tokens.

    Returns:
        list: List of stemmed tokens.
    """
    out = []
    for token in tokens:
        out.extend([t.lemma_ for t in NLP_LEMMATIZER(token)])
    return out


def remove_emojis_from_text(text):
    """
    Removes emojis from a given text.

    Args:
        text (str): The input text.

    Returns:
        str: The text without emojis.

    """
    emoji_pattern = re.compile(
        pattern="["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U00002500-\U00002BEF"  # Chinese/Japanese/Korean characters
                "\U00002702-\U000027B0"
                "\U00002702-\U000027B0"
                "\U000024C2-\U0001F251"
                "\U0001f926-\U0001f937"
                "\U00010000-\U0010ffff"
                "\u2640-\u2642"
                "\u2600-\u2B55"
                "\u200d"
                "\u23cf"
                "\u23e9"
                "\u231a"
                "\ufe0f"  # dingbats
                "\u3030"
                "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


def remove_non_ascii_from_text(words: list[str]) -> list[str]:
    """
    Removes all non-ASCII characters from a list of words.

    Args:
        words (list[str]): The input tokens.

    Returns:
        list[str]: The tokens without non-ASCII characters.

    """
    out = []
    for word in words:
        if word.isnumeric():
            out.append(word)
        elif word.isascii():
            out.append(word)
        else:
            try:
                if detect(word) in ['de', 'en']:
                    out.append(word)
            except Exception as _:
                pass
    return out


def remove_umlaute(tokens):
    """
    Remove umlaut characters from the tokens.

    Args:
        tokens (list[str]): List of tokens.

    Returns:
        list[str]: List of tokens with umlaut characters replaced.

    Example:
        tokens = ['über', 'müssen', 'hören']
        remove_umlaute(tokens)
        Output: ['uber', 'mussen', 'horen']
    """
    return [
        t.lower().replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "s").replace("ã¼", "u").replace(
            "Ã¼", "u") for t
        in tokens]


def remove_very_long_words(tokens, threshold=int(os.getenv("REMOVE_LONG_WORD_THRESHOLD"))):
    """
    Remove very long words from the tokens.

    Args:
        tokens (list[str]): List of tokens.
        threshold (int, optional): Maximum length of words to keep. Defaults to the value defined in the environment variable "REMOVE_LONG_WORD_THRESHOLD".

    Returns:
        list[str]: List of tokens without very long words.

    Example:
        tokens = ['apple', 'banana', 'internationalization', 'localization']
        remove_very_long_words(tokens)
        Output: ['apple', 'banana']
    """
    return [t for t in tokens if len(t) < threshold]


def lower_and_strip(tokens):
    """
    Convert tokens to lowercase and strip leading/trailing whitespaces.

    Args:
        tokens (list[str]): List of tokens.

    Returns:
        list[str]: List of tokens converted to lowercase and stripped.

    Example:
        tokens = [' Apple  ', 'BaNaNa', '  ORANGE']
        lower_and_strip(tokens)
        Output: ['apple', 'banana', 'orange']
    """
    return [t.lower().strip() for t in tokens]


def unify_tuebingen(tokens):
    """
    Unify the spelling of 'tuebingen' to 'tubingen' in the tokens.

    Args:
        tokens (list[str]): List of tokens.

    Returns:
        list[str]: List of tokens with 'tuebingen' replaced by 'tubingen'.

    Example:
        tokens = ['tuebingen', 'university', 'is', 'great']
        unify_tuebingen(tokens)
        Output: ['tubingen', 'university', 'is', 'great']
    """
    return [t.replace("tuebingen", "tubingen") for t in tokens]


def tokenize(text: str) -> list[str]:
    """
    Tokenize the input text into a list of words.

    Args:
        text (str): Input text to be tokenized.

    Returns:
        list[str]: List of tokens (words) extracted from the text.

    Example:
        text = "Hello, how are you?"
        tokenize(text)
        Output: ['Hello', ',', 'how', 'are', 'you', '?']
    """
    return [word.text for word in NLP_TOKENIZER(text)]


def remove_empty_token(words: list[str]) -> list[str]:
    """
    Remove empty tokens from the list of words.

    Args:
        words (list[str]): List of words.

    Returns:
        list[str]: List of words without empty tokens.

    Example:
        words = ['apple', '', 'banana', '  ', 'orange']
        remove_empty_token(words)
        Output: ['apple', 'banana', 'orange']
    """
    return [word for word in words if len(word) > 0]


def remove_stop_words(words: list[str]) -> list[str]:
    """
    Remove stop words from the list of words.

    Args:
        words (list[str]): List of words.

    Returns:
        list[str]: List of words without stop words.

    Example:
        words = ['apple', 'banana', 'is', 'a', 'fruit']
        remove_stop_words(words)
        Output: ['apple', 'banana', 'fruit']
    """
    return [word for word in words if word not in ENGLISH_STOP_WORDS]


def remove_punctation(words: list[str]) -> list[str]:
    """
    Remove punctuation from the list of words.

    Args:
        words (list[str]): List of words.

    Returns:
        list[str]: List of words without punctuation.

    Example:
        words = ['hello', ',', 'world', '!', 'nice']
        remove_punctation(words)
        Output: ['hello', 'world', 'nice']
    """
    return [word for word in words if word not in punctuation_characters()]


def preprocess_text_and_tokenize(text: str) -> list[str]:
    """
    Preprocesses a text sequence by performing tokenization and filtering out stop words and punctuation.

    Args:
        text (str): Input text sequence.

    Returns:
        list[str]: List of preprocessed tokens.
    """
    text = html.unescape(text)

    text = remove_emojis_from_text(text)

    text = remove_hyperlinks_from_text(text)

    words = tokenize(text)
    #print(("#" * 20) + f"Tokenize and lower case {words}", file=sys.stderr)

    words = lower_and_strip(words)
    #print(("#" * 20) + f"Lower and strip {words}", file=sys.stderr)

    words = remove_empty_token(words)
    #print(("#" * 20) + f"Remove empty tokens {words}", file=sys.stderr)

    words = remove_umlaute(words)
    #print(("#" * 20) + f"Remove german umlaute {words}", file=sys.stderr)

    words = remove_stop_words(words)
    #print(("#" * 20) + f"Remove EN stop words {words}", file=sys.stderr)

    words = remove_non_ascii_from_text(words)
    #print(("#" * 20) + f"Remove non-ascii {words}", file=sys.stderr)

    words = remove_punctation(words)
    #print(("#" * 20) + f"Remove punctuation {words}", file=sys.stderr)

    words = stem_words_of_tokens(words)
    #print(("#" * 20) + f"Stem english {words}", file=sys.stderr)

    words = remove_umlaute(words)  # Remove Umlaute, again. Yes, intended!
    #print(("#" * 20) + f"Remove german umlaute {words}", file=sys.stderr)

    words = remove_very_long_words(words)
    #print(("#" * 20) + f"Remove very long words {words}", file=sys.stderr)

    # Remove punctuation, again. Yes, intended!
    words = remove_punctation(words)
    #print(("#" * 20) + f"Remove punctuation {words}", file=sys.stderr)

    words = unify_tuebingen(words)  # Only one university name
    #print(("#" * 20) + f"Unify tuebingen {words}", file=sys.stderr)

    return words


def get_title_from_html(html):
    """
    Extracts the title from HTML content.

    Args:
        html (str): HTML content.

    Returns:
        str: Title of the HTML content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string
    return title


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


def is_text_url(url):
    """
    Check if a URL is a "normal" text URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a "normal" text URL, False otherwise.
    """
    file_extension = url.split('.')[-1].lower()
    return (url.startswith('http://') or url.startswith('https://') or url.startswith(
        'www.')) and file_extension not in CRAWL_EXCLUDED_EXTENSIONS


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


def strip_text_title_and_tags_from_html(html_content: str) -> str:
    """
    Extracts plain text from HTML content.

    Args:
        html_content (str): HTML content.

    Returns:
        str: Plain text extracted from HTML.
    """
    body = BeautifulSoup(html_content, 'html.parser').get_text(separator=' ')
    tags = ["title", "meta"]
    tags_text = [extract_content_from_tag(html_content, tag) for tag in tags]
    tags_text = " ".join(tags_text)
    return body + " " + tags_text


def is_url_and_server_allowed(url: str, server: str) -> bool:
    """
    Checks if the URL and server are allowed based on predefined white and blacklists.

    Args:
        url (str): The URL to check.
        server (str): The server/domain to check.

    Returns:
        bool: True if the URL and server are allowed, False otherwise.
    """
    return (server not in CRAWL_BLACK_LIST) or ("bingen" in url)


def is_url_not_on_black_list(server: str) -> bool:
    """
    Checks if the URL and server are allowed based on blacklists.

    Args:
        server (str): The server/domain to check.

    Returns:
        bool: True if the URL and server are allowed, False otherwise.
    """
    return server not in CRAWL_BLACK_LIST


def is_url_relevant(url: str) -> bool:
    """
    Classifies the relevance of a URL based on several criteria.

    Args:
        url (str): The URL to classify.

    Returns:
        bool: True if the URL is relevant, False otherwise.
    """
    server = get_domain_name_without_subdomain_and_suffix_from_url(url)
    is_not_media = is_text_url(url)
    is_not_block = is_url_and_server_allowed(url, server)
    return is_not_media and is_not_block


def is_job_relevant(job) -> bool:
    """
    Classifies the relevance of a job based on several criteria. A job is either relevant if
    - It's a seed job and the domain is not blocked.
    - Or the URL is relevant.

    Args:
        job (Job): The job to classify.
    return:
        bool: True if the job is relevant, False otherwise.
    """
    return (job.bfs_layer < 2 and is_url_not_on_black_list(
        job.server)) or is_url_relevant(job.url)


def do_tokens_contain_tuebingen(tokens: list[str]):
    """
    Checks if a list of tokens contains variations of the word "Tübingen".

    Args:
        tokens (list): List of tokens.

    Returns:
        bool: True if the word variations of "Tübingen" are present in the tokens, False otherwise.
    """
    for tuebingen in INVERTED_INDEX_TUEBINGEN_WRITING_STYLES:
        for token in tokens:
            if tuebingen in token:
                return True
    return False


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


def get_domain_name_from_url(url: str) -> str:
    """
    Extracts the domain name from a given URL.

    Args:
        url (str): Input URL.

    Returns:
        str: Extracted domain name.
    """
    return urlparse(url).netloc.replace("www.", "")


def get_domain_name_without_subdomain_from_url(url: str):
    """
    Extracts the domain name without subdomain from a given URL.

    Args:
        url (str): Input URL.

    Returns:
        str: Extracted domain name without subdomain.
    """
    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"


def get_domain_name_without_subdomain_and_suffix_from_url(url: str):
    """
    Extracts the domain name without subdomain and suffix from a given URL.

    Args:
        url (str): Input URL.

    Returns:
        str: Extracted domain name without subdomain and suffix.
    """
    return tldextract.extract(url).domain


def get_logger(name: str, log_file_name: str = None,
               max_file_size: int = 10 * 1024 * 1024, backup_count: int = 20):
    """
    Creates a logger instance with the specified name, log file name, and file size limit.

    Args:
        name (str): Logger name.
        log_file_name (str): Log file name.
        max_file_size (int): Maximum file size in bytes (default is 10 MB).
        backup_count (int): Number of backup log files to keep (default is 20).

    Returns:
        logging.Logger: Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(filename)s:%(lineno)d - %(message)s',
        '%d-%m %H:%M')

    if log_file_name is not None:
        file_handler = RotatingFileHandler(
            log_file_name,
            maxBytes=max_file_size,
            backupCount=backup_count)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(console_handler)
    console_handler.setFormatter(formatter)

    return logger
