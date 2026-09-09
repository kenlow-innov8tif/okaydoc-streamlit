import unittest
from unittest.mock import Mock, patch

import requests

from utils.api_client import ApiRequestError, post_json, post_multipart


class ApiClientTests(unittest.TestCase):
    @patch("utils.api_client.requests.post")
    def test_json_post_uses_default_timeout(self, mock_post):
        response = Mock()
        mock_post.return_value = response

        result = post_json("https://example.test/api", {"image": "encoded"})

        self.assertIs(result, response)
        mock_post.assert_called_once_with(
            "https://example.test/api",
            json={"image": "encoded"},
            timeout=30,
        )

    @patch("utils.api_client.requests.post")
    def test_multipart_post_uses_provided_timeout(self, mock_post):
        response = Mock()
        mock_post.return_value = response
        files = {"image": Mock()}

        result = post_multipart(
            "https://example.test/api",
            {"journeyId": "journey"},
            files,
            timeout=10,
        )

        self.assertIs(result, response)
        mock_post.assert_called_once_with(
            "https://example.test/api",
            data={"journeyId": "journey"},
            files=files,
            timeout=10,
        )

    @patch("utils.api_client.requests.post", side_effect=requests.Timeout)
    def test_timeout_has_safe_user_message(self, mock_post):
        with self.assertRaisesRegex(ApiRequestError, "timed out"):
            post_json("https://example.test/api", {})

    @patch("utils.api_client.requests.post", side_effect=requests.ConnectionError)
    def test_connection_failure_has_safe_user_message(self, mock_post):
        with self.assertRaisesRegex(ApiRequestError, "Could not connect"):
            post_json("https://example.test/api", {})
