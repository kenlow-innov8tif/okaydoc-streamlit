"""Environment-specific API configuration."""


DEMO_ENVIRONMENT = "DEMO"
PRODUCTION_ENVIRONMENT = "PRODUCTION"

DEMO_BASE_URL = "https://ekycportaldemo.innov8tif.com"
PRODUCTION_BASE_URL = "https://ekycportal.innov8tif.com"


def get_base_url(environment):
    if environment == PRODUCTION_ENVIRONMENT:
        return PRODUCTION_BASE_URL
    return DEMO_BASE_URL


def get_environment_for_toggle(production_enabled):
    if production_enabled:
        return PRODUCTION_ENVIRONMENT
    return DEMO_ENVIRONMENT
