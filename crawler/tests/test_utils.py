import unittest

from crawler import utils


class TestUtils(unittest.TestCase):
    def test_preprocess_and_tokenize(self):
        text = "From the Neckar Bridge you have the most beautiful view of TÃ¼bingen."
        tokens = utils.preprocess_text_and_tokenize(text)
        self.assertTrue("tubingen" in tokens)


if __name__ == '__main__':
    unittest.main()
