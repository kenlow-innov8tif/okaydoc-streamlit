import unittest
from unittest.mock import Mock, patch

from api.submitters import (
    request_journey_id,
    submit_okaydoc_api,
    submit_okaydoc_passport_api,
    submit_okayface_api,
    submit_okayid_api,
    submit_okaylive_api,
)


class SubmitterTests(unittest.TestCase):
    @patch("api.submitters.post_json")
    def test_journey_request_uses_expected_endpoint_and_payload(self, mock_post):
        request_journey_id("https://example.test/", "user", "password")

        mock_post.assert_called_once_with(
            "https://example.test/api/ekyc/journeyid",
            {"username": "user", "password": "password"},
        )

    @patch("api.submitters.post_json")
    def test_okayid_submission_adds_images_without_mutating_parameters(self, mock_post):
        api_params = {"imageFormat": "JPG"}

        submit_okayid_api(
            "https://example.test",
            "journey",
            "front",
            api_params,
            "back",
        )

        mock_post.assert_called_once_with(
            "https://example.test/api/ekyc/okayid",
            {
                "imageFormat": "JPG",
                "journeyId": "journey",
                "base64ImageString": "front",
                "backImage": "back",
            },
        )
        self.assertEqual(api_params, {"imageFormat": "JPG"})

    @patch("api.submitters.post_json")
    def test_okayid_submission_omits_optional_back_image(self, mock_post):
        submit_okayid_api("https://example.test", "journey", "front", {})

        self.assertNotIn("backImage", mock_post.call_args.args[1])

    @patch("api.submitters.post_json")
    def test_okaydoc_submission_uses_nonpassport_payload(self, mock_post):
        submit_okaydoc_api("https://example.test", "journey", "image", {"docType": "mykad"})

        mock_post.assert_called_once_with(
            "https://example.test/api/ekyc/okaydoc",
            {
                "docType": "mykad",
                "journeyId": "journey",
                "type": "nonpassport",
                "idImageBase64Image": "image",
            },
        )

    @patch("api.submitters.post_json")
    def test_passport_submission_includes_full_image_only_when_supplied(self, mock_post):
        submit_okaydoc_passport_api("https://example.test", "journey", "OTHER", "half")
        submit_okaydoc_passport_api("https://example.test", "journey", "OTHER", "half", "full")

        self.assertEqual(mock_post.call_count, 2)
        self.assertNotIn("fullSizeImage", mock_post.call_args_list[0].args[1])
        self.assertEqual(mock_post.call_args_list[1].args[1]["fullSizeImage"], "full")

    @patch("api.submitters.post_multipart")
    def test_face_and_live_submissions_use_expected_multipart_data(self, mock_post):
        files = {"image": Mock()}
        submit_okayface_api("https://example.test", "journey", "true", files)
        submit_okaylive_api("https://example.test", "journey", files)

        self.assertEqual(mock_post.call_count, 2)
        self.assertEqual(mock_post.call_args_list[0].args[0], "https://example.test/api/ekyc/okayface/v1-1")
        self.assertEqual(mock_post.call_args_list[0].args[1], {"journeyId": "journey", "livenessDetection": "true"})
        self.assertEqual(mock_post.call_args_list[1].args[0], "https://example.test/api/ekyc/okaylive")
        self.assertEqual(mock_post.call_args_list[1].args[1], {"journeyId": "journey"})
