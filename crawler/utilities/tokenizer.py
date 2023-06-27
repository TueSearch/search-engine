"""

"""
import functools
import os
import re
import unicodedata
import html

import spacy
from dotenv import load_dotenv
from langdetect import detect
from nltk.corpus import stopwords

# Load environment variables and other stuff
load_dotenv()

# Set up global variables
NLP_TOKENIZER = spacy.load(os.getenv("SPACY_TOKENIZER_MODEL"))
NLP_LEMMATIZER = spacy.load(os.getenv("SPACY_ENGLISH_LEMMATIZATION_MODEL"))
ENGLISH_STOP_WORDS = set(stopwords.words('english'))


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
    # print(("#" * 20) + f"Tokenize and lower case {words}", file=sys.stderr)

    words = lower_and_strip(words)
    # print(("#" * 20) + f"Lower and strip {words}", file=sys.stderr)

    words = remove_empty_token(words)
    # print(("#" * 20) + f"Remove empty tokens {words}", file=sys.stderr)

    words = remove_umlaute(words)
    # print(("#" * 20) + f"Remove german umlaute {words}", file=sys.stderr)

    words = remove_stop_words(words)
    # print(("#" * 20) + f"Remove EN stop words {words}", file=sys.stderr)

    words = remove_non_ascii_from_text(words)
    # print(("#" * 20) + f"Remove non-ascii {words}", file=sys.stderr)

    words = remove_punctation(words)
    # print(("#" * 20) + f"Remove punctuation {words}", file=sys.stderr)

    words = stem_words_of_tokens(words)
    # print(("#" * 20) + f"Stem english {words}", file=sys.stderr)

    words = remove_umlaute(words)  # Remove Umlaute, again. Yes, intended!
    # print(("#" * 20) + f"Remove german umlaute {words}", file=sys.stderr)

    words = remove_very_long_words(words)
    # print(("#" * 20) + f"Remove very long words {words}", file=sys.stderr)

    # Remove punctuation, again. Yes, intended!
    words = remove_punctation(words)
    # print(("#" * 20) + f"Remove punctuation {words}", file=sys.stderr)

    words = unify_tuebingen(words)  # Only one university name
    # print(("#" * 20) + f"Unify tuebingen {words}", file=sys.stderr)

    return words
