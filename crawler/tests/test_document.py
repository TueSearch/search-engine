"""Test utility"""
import unittest

from crawler.models.document import Document


class TestDocument(unittest.TestCase):
    """Test Document"""

    def test_python_db_values(self):
        """
        Test if python db values are correct.
        """
        document = Document()
        self.assertTrue(isinstance(document.h1, str))
        self.assertTrue(isinstance(document.h1_tokens, list))

        self.assertTrue(isinstance(document.h2, str))
        self.assertTrue(isinstance(document.h2_tokens, list))

        self.assertTrue(isinstance(document.h3, str))
        self.assertTrue(isinstance(document.h3_tokens, list))

        self.assertTrue(isinstance(document.h4, str))
        self.assertTrue(isinstance(document.h4_tokens, list))

        self.assertTrue(isinstance(document.h5, str))
        self.assertTrue(isinstance(document.h5_tokens, list))

        self.assertTrue(isinstance(document.h6, str))
        self.assertTrue(isinstance(document.h6_tokens, list))

        self.assertTrue(isinstance(document.body, str))
        self.assertTrue(isinstance(document.body_tokens, list))

        self.assertTrue(isinstance(document.title, str))
        self.assertTrue(isinstance(document.title_tokens, list))

        self.assertTrue(isinstance(document.meta_description, str))
        self.assertTrue(isinstance(document.meta_description_tokens, list))

        self.assertTrue(isinstance(document.meta_keywords, str))
        self.assertTrue(isinstance(document.meta_keywords_tokens, list))

        self.assertTrue(isinstance(document.meta_author, str))
        self.assertTrue(isinstance(document.meta_author_tokens, list))

        self.assertTrue(isinstance(document.links, list))
        self.assertTrue(isinstance(document.relevant_links, list))


if __name__ == '__main__':
    unittest.main()
