"""Test utility"""
import unittest
from crawler import utils


class TestUtils(unittest.TestCase):
    def test_tokenize(self):
        """Test if html is escaped"""
        text = "Tübingen (German) is a traditional university city in central Baden-Württemberg, Germany. In the season of autumn."
        tokens = utils.text.tokenize(text)
        self.assertTrue("tubingen" in tokens[0])


if __name__ == '__main__':
    unittest.main()
