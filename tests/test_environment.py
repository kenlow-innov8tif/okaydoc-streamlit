import unittest

from utils.environment import (
    DEMO_BASE_URL,
    DEMO_ENVIRONMENT,
    PRODUCTION_BASE_URL,
    PRODUCTION_ENVIRONMENT,
    get_environment_for_toggle,
    get_base_url,
)


class EnvironmentTests(unittest.TestCase):
    def test_demo_environment_uses_demo_url(self):
        self.assertEqual(get_base_url(DEMO_ENVIRONMENT), DEMO_BASE_URL)

    def test_production_environment_uses_production_url(self):
        self.assertEqual(get_base_url(PRODUCTION_ENVIRONMENT), PRODUCTION_BASE_URL)

    def test_unknown_environment_defaults_to_demo_url(self):
        self.assertEqual(get_base_url("unknown"), DEMO_BASE_URL)

    def test_enabled_toggle_selects_production(self):
        self.assertEqual(get_environment_for_toggle(True), PRODUCTION_ENVIRONMENT)

    def test_disabled_toggle_selects_demo(self):
        self.assertEqual(get_environment_for_toggle(False), DEMO_ENVIRONMENT)
