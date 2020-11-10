import requests_mock
import urllib

from django.test import TestCase, override_settings

from .track import API_VERSION, GOOGLE_ANALYTICS_ENDPOINT, track_event


FAKE_GA_ID = "GTM-GA-id"


@override_settings(HELPDESK_GA_GTM=FAKE_GA_ID)
class TrackTestCase(TestCase):

    @requests_mock.Mocker()
    def test_track_event(self, mock_requests):
        mock_requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
        )

        track_event(
            "test_category",
            "test_action",
        )
        request = mock_requests.request_history[0]
        data = urllib.parse.parse_qs(request.text)
        self.assertEqual(
            data["v"],
            [API_VERSION],
        )
        self.assertEqual(
            data["tid"],
            [FAKE_GA_ID],
        )
        self.assertEqual(
            data["t"],
            ["event"],
        )
        self.assertEqual(
            data["ec"],
            ["test_category"],
        )
        self.assertEqual(
            data["ea"],
            ["test_action"],
        )
        self.assertNotIn("el", data)
        self.assertNotIn("ev", data)

        track_event(
            "test_category_2",
            "test_action_2",
            "test_label",
            "test_value",
        )
        request = mock_requests.request_history[1]
        data = urllib.parse.parse_qs(request.text)
        self.assertEqual(
            data["v"],
            [API_VERSION],
        )
        self.assertEqual(
            data["tid"],
            [FAKE_GA_ID],
        )
        self.assertEqual(
            data["t"],
            ["event"],
        )
        self.assertEqual(
            data["ec"],
            ["test_category_2"],
        )
        self.assertEqual(
            data["ea"],
            ["test_action_2"],
        )
        self.assertEqual(
            data["el"],
            ["test_label"],
        )
        self.assertEqual(
            data["ev"],
            ["test_value"],
        )

    @requests_mock.Mocker()
    def test_unique_user_id(self, mock_requests):
        mock_requests.post(
            GOOGLE_ANALYTICS_ENDPOINT,
        )

        user_ids = []

        for i in range(20):
            track_event(
                "test_category",
                "test_action",
            )
            request = mock_requests.request_history[i]
            data = urllib.parse.parse_qs(request.text)
            user_ids.append(data["cid"][0])

        self.assertEqual(
            len(user_ids),
            len(set(user_ids)),
        )
