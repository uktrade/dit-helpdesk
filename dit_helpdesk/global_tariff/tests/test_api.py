import requests_mock

from django.test import TestCase

from ..api import (
    get_commodity_data,
    get_commodity_code_data,
    MultipleResultsError,
    NoResultError,
    ROOT_URL,
)


class GetCommodityCpdeDataTestCase(TestCase):

    @requests_mock.Mocker()
    def test_get_commodity_code_data_test(self, mock_requests):
        code = "123456"
        test_response = [{
            'atq_applies': False,
            'cet_applies_until_trade_remedy_transition_reviews_concluded': False,
            'cet_duty_rate': '12.0%',
            'change': 'No change',
            'commodity': '123456',
            'description': 'Foo bar baz',
            'suspension_applies': False,
            'trade_remedy_applies': False,
            'ukgt_duty_rate': '12.0%',
        }]
        mock_requests.get(
            f"{ROOT_URL}?q={code}",
            json=test_response
        )
        output = get_commodity_code_data(code)

        self.assertEqual(output, test_response)


class GetCommodityDataTestCase(TestCase):

    def _get_test_commodity_response(self, commodity, description):
        return {
            'atq_applies': False,
            'cet_applies_until_trade_remedy_transition_reviews_concluded': False,
            'cet_duty_rate': '12.0%',
            'change': 'No change',
            'commodity': commodity,
            'description': description,
            'suspension_applies': False,
            'trade_remedy_applies': False,
            'ukgt_duty_rate': '12.0%',
        }

    @requests_mock.Mocker()
    def test_commodity_has_direct_result(self, mock_requests):
        code = "123456"
        hierarchy_codes = [code, code[:-2], code[:-4]]

        test_response = [
            self._get_test_commodity_response(hierarchy_codes[0], f"Desc for {hierarchy_codes[0]}"),
        ]
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[0]}",
            json=test_response
        )
        commodity_code, output = get_commodity_data(hierarchy_codes)

        self.assertEqual(commodity_code, hierarchy_codes[0])
        self.assertEqual(output, test_response[0])

    @requests_mock.Mocker()
    def test_commodity_has_direct_ancestor_result(self, mock_requests):
        code = "123456"
        hierarchy_codes = [code, code[:-2], code[:-4]]

        test_no_data_response = []
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[0]}",
            json=test_no_data_response,
        )

        test_response = [
            self._get_test_commodity_response(hierarchy_codes[1], f"Desc for {hierarchy_codes[1]}"),
        ]
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[1]}",
            json=test_response,
        )

        commodity_code, output = get_commodity_data(hierarchy_codes)

        self.assertEqual(commodity_code, hierarchy_codes[1])
        self.assertEqual(output, test_response[0])

    @requests_mock.Mocker()
    def test_commodity_has_indirect_ancestor_result(self, mock_requests):
        code = "123456"
        hierarchy_codes = [code, code[:-2], code[:-4]]

        test_no_data_response = []

        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[0]}",
            json=test_no_data_response,
        )
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[1]}",
            json=test_no_data_response,
        )

        test_response = [
            self._get_test_commodity_response(hierarchy_codes[2], f"Desc for {hierarchy_codes[2]}"),
        ]
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[2]}",
            json=test_response,
        )

        commodity_code, output = get_commodity_data(hierarchy_codes)

        self.assertEqual(commodity_code, hierarchy_codes[2])
        self.assertEqual(output, test_response[0])

    @requests_mock.Mocker()
    def test_commodity_has_no_results(self, mock_requests):
        code = "123456"
        hierarchy_codes = [code, code[:-2], code[:-4]]

        test_no_data_response = []

        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[0]}",
            json=test_no_data_response,
        )
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[1]}",
            json=test_no_data_response,
        )
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[2]}",
            json=test_no_data_response,
        )

        with self.assertRaises(NoResultError):
            get_commodity_data(hierarchy_codes)

    @requests_mock.Mocker()
    def test_commodity_has_multiple_results(self, mock_requests):
        code = "123456"
        hierarchy_codes = [code, code[:-2], code[:-4]]

        test_no_data_response = []
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[0]}",
            json=test_no_data_response,
        )
        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[1]}",
            json=test_no_data_response,
        )

        mock_requests.get(
            f"{ROOT_URL}?q={hierarchy_codes[2]}",
            json=[
                self._get_test_commodity_response("01", "01 result"),
                self._get_test_commodity_response("02", "02 result"),
            ],
        )

        with self.assertRaises(MultipleResultsError):
            get_commodity_data(hierarchy_codes)
