"""Payload builders and submitters for the eKYC API endpoints."""

from utils.api_client import post_json, post_multipart


def request_journey_id(base_url, username, password):
    return post_json(
        f"{base_url.rstrip('/')}/api/ekyc/journeyid",
        {"username": username, "password": password},
    )


def submit_okayid_api(base_url, journey_id, front_image_base64, api_params, back_image_base64=None):
    payload = {
        **api_params,
        "journeyId": journey_id,
        "base64ImageString": front_image_base64,
    }
    if back_image_base64 is not None:
        payload["backImage"] = back_image_base64
    return post_json(f"{base_url.rstrip('/')}/api/ekyc/okayid", payload)


def submit_okaydoc_api(base_url, journey_id, image_base64, api_params):
    payload = {
        **api_params,
        "journeyId": journey_id,
        "type": "nonpassport",
        "idImageBase64Image": image_base64,
    }
    return post_json(f"{base_url.rstrip('/')}/api/ekyc/okaydoc", payload)


def submit_okaydoc_passport_api(base_url, journey_id, country, half_image_base64, full_image_base64=None):
    payload = {
        "journeyId": journey_id,
        "type": "passport",
        "country": country,
        "halfSizeImage": half_image_base64,
    }
    if full_image_base64 is not None:
        payload["fullSizeImage"] = full_image_base64
    return post_json(f"{base_url.rstrip('/')}/api/ekyc/okaydoc", payload)


def submit_okayface_api(base_url, journey_id, liveness_detection, files):
    return post_multipart(
        f"{base_url.rstrip('/')}/api/ekyc/okayface/v1-1",
        {"journeyId": journey_id, "livenessDetection": liveness_detection},
        files,
    )


def submit_okaylive_api(base_url, journey_id, files):
    return post_multipart(
        f"{base_url.rstrip('/')}/api/ekyc/okaylive",
        {"journeyId": journey_id},
        files,
    )
