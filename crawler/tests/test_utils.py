"""Test utility"""
import unittest

import langdetect

from crawler import utils
from crawler.relevance_classification import url_relevance


class TestUtils(unittest.TestCase):
    """Test utility"""

    def test_tokenize(self):
        """Test if html is escaped"""
        text = "Tübingen (German) is a traditional university city in central Baden-Württemberg, Germany. In the season of autumn."
        tokens = utils.text.advanced_tokenize_with_pos(text)
        self.assertTrue("tubingen" in tokens[0])

    def test_is_url_relevant(self):
        """Test if url is relevant"""
        self.assertFalse(url_relevance.is_url_relevant(
            "https://javascript:linkTo_UnCryptMailto(%27ocknvq%2CkphqBvhy0wpk%5C%2Fvwgdkpigp0fg%27);/"))
        self.assertFalse(url_relevance.is_url_relevant(
            "tel:+4970712975570"))
        self.assertTrue(url_relevance.is_url_relevant(
            "https://uni-tuebingen.de/"))

    def test_tokenize_url(self):
        """Test if url is english"""
        self.assertEqual("en", langdetect.detect(" ".join(utils.url.tokenize_url(
            "https://tuebingenresearchcampus.com/en/research-in-tuebingen/tnc/neuro-campus-initiatives/"))))


if __name__ == '__main__':
    unittest.main()
