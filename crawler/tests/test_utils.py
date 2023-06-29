"""Test utility"""
import unittest
from crawler import utils
from crawler.relevance_classification import url_relevance


class TestUtils(unittest.TestCase):
    """Test utility"""

    def test_tokenize(self):
        """Test if html is escaped"""
        text = "Tübingen (German) is a traditional university city in central Baden-Württemberg, Germany. In the season of autumn."
        tokens = utils.text.tokenize(text)
        self.assertTrue("tubingen" in tokens[0])

    def test_is_url_relevant(self):
        self.assertFalse(url_relevance.is_url_relevant(
            "https://javascript:linkTo_UnCryptMailto(%27ocknvq%2CkphqBvhy0wpk%5C%2Fvwgdkpigp0fg%27);/"))
        self.assertFalse(url_relevance.is_url_relevant(
            "tel:+4970712975570"))
        self.assertTrue(url_relevance.is_url_relevant(
            "https://uni-tuebingen.de/"))


if __name__ == '__main__':
    unittest.main()
