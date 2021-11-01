import requests_mock

from django.test import TestCase
from string import ascii_lowercase
from trade_tariff_service.SynonymBuilder import SynonymBuilder, MissingSynonymsException


class SynonymBuilderTestCase(TestCase):
    """
    Test Synonym Builder class
    """

    def setUp(self):
        self.synonym_builder = SynonymBuilder()

    @requests_mock.Mocker()
    def test_get_list_success(self, mocked_requests):

        # Have to stub every call, so loop through alphabet get them all out,
        # just replacing a and b with the mock data for testing.
        for letter in ascii_lowercase:
            if letter == "a":
                mocked_requests.get(
                    "https://www.trade-tariff.service.gov.uk/api/v2/search_references.json?query%5Bletter%5D=a",
                    json={
                        "data": [
                            {
                                "id": "1111",
                                "attributes": {
                                    "referenced_class": "Heading",
                                    "referenced_id": "0101",
                                    "title": "Unicorns",
                                },
                            },
                            {
                                "id": "1114",
                                "attributes": {
                                    "referenced_class": "Commodity",
                                    "referenced_id": "01070111",
                                    "title": "Copies Of Shaq-Fu",
                                },
                            },
                        ]
                    },
                )
            elif letter == "b":
                mocked_requests.get(
                    "https://www.trade-tariff.service.gov.uk/api/v2/search_references.json?query%5Bletter%5D=b",
                    json={
                        "data": [
                            {
                                "id": "1112",
                                "attributes": {
                                    "referenced_class": "Heading",
                                    "referenced_id": "0102",
                                    "title": "John Cena T Shirts",
                                },
                            },
                            {
                                "id": "1113",
                                "attributes": {
                                    "referenced_class": "Chapter",
                                    "referenced_id": "01",
                                    "title": "Increasingly Obscure Funko Pop Figures",
                                },
                            },
                        ]
                    },
                )
            else:
                mocked_requests.get(
                    f"https://www.trade-tariff.service.gov.uk/api/v2/search_references.json?query%5Bletter%5D={letter}",
                    json={"data": []},
                )

        resp = self.synonym_builder.get_synonyms_list()

        # Response should only contain the 4 digit codes
        self.assertEqual(resp, [["01.01", "Unicorns"], ["01.02", "John Cena T Shirts"]])

        # Response should not contain 2 digit codes
        self.assertNotIn(str(resp), "Increasingly Obscure Funko Pop Figures")

        # Response should not contain more than 2 digit codes
        self.assertNotIn(str(resp), "Copies Of Shaq-Fu")

    @requests_mock.Mocker()
    def test_get_list_no_synonyms(self, mocked_requests):

        for letter in ascii_lowercase:
            mocked_requests.get(
                f"https://www.trade-tariff.service.gov.uk/api/v2/search_references.json?query%5Bletter%5D={letter}",
                json={"data": []},
            )

        with self.assertRaises(MissingSynonymsException):
            self.synonym_builder.get_synonyms_list()
