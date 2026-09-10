import unittest

from utils.api_parameters import build_okaydoc_api_params


class OkayDocApiParametersTests(unittest.TestCase):
    def test_builder_uses_current_values_for_every_field(self):
        params = build_okaydoc_api_params(
            "passport",
            "8",
            "false",
            "true",
            "false",
            "true",
            "false",
            "true",
            "false",
            "true",
            "false",
            "true",
            "false",
            "true",
        )

        self.assertEqual(params["docType"], "passport")
        self.assertEqual(params["version"], "8")
        self.assertEqual(params["landmarkCheck"], "false")
        self.assertEqual(params["qualityCheckDetection"], "true")
        self.assertEqual(len(params), 14)
