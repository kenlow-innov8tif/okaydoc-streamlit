"""HTTP helpers that provide consistent timeout and failure behaviour."""

import requests


DEFAULT_TIMEOUT_SECONDS = 30


class ApiRequestError(Exception):
    """A safe, user-facing error raised when an API request cannot complete."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def post_json(url, payload, timeout=DEFAULT_TIMEOUT_SECONDS):
    return _post(url, json=payload, timeout=timeout)


def post_multipart(url, data, files, timeout=DEFAULT_TIMEOUT_SECONDS):
    return _post(url, data=data, files=files, timeout=timeout)


def _post(url, **kwargs):
    try:
        return requests.post(url, **kwargs)
    except requests.Timeout as error:
        raise ApiRequestError("The API request timed out. Please try again.") from error
    except requests.ConnectionError as error:
        raise ApiRequestError("Could not connect to the API. Check your network and environment.") from error
    except requests.RequestException as error:
        raise ApiRequestError("The API request could not be completed. Please try again.") from error
