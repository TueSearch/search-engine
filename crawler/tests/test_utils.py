import unittest

from crawler import utils


class TestUtils(unittest.TestCase):
    def test_tokenize(self):
        text = "ï»¿ ETRA 2023: ACM Symposium on Eye Tracking Research & Applications Local Attractions Neckarfront The Neckarfront is the most famous photo motif of the university town. From the Neckar Bridge you have the most beautiful view of TÃ¼bingen. To enjoy the entire panorama from different angles, we recommend a walk along the plane tree avenue on the idyllic Neckar Island or, even better, a punting trip. Old Town Take a stroll through the pitoresque alleys of the medieval old town. Take a look around the impressive market square, with its ensemble of buildings from the 15th and 16th centuries and other highlights like the Holzmarkt, the Burse and the Ammergasse. Public tours are offered on Saturdays. To learn more about the history of TÃ¼bingen you can visit the city museum with free admission. HÃ¶lderlin Tower & Museum The HÃ¶lderlin Tower: yellow with a pointed roof, idyllically situated on the Neckar River, is one of TÃ¼bingen's landmarks. For 36 years, the tower room on the second floor"
        self.assertTrue("tuebingen" in utils.remove_umlaute(text))


if __name__ == '__main__':
    unittest.main()
