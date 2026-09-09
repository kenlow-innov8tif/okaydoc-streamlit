"""Helpers for preparing images for API payloads."""

import base64
import io


def encode_image_base64(original_bytes, edited_image, is_edited, image_format, **save_options):
    """Return original upload bytes unless image edits require re-encoding."""
    if not is_edited:
        return base64.b64encode(original_bytes).decode("utf-8"), "Original upload"

    buffered = io.BytesIO()
    edited_image.save(buffered, format=image_format, **save_options)
    return base64.b64encode(buffered.getvalue()).decode("utf-8"), "Edited image"


def get_base64_decoded_size(encoded_image):
    """Return the decoded byte size of a Base64 value without exposing its data."""
    if not encoded_image:
        return 0

    padding = encoded_image[-2:].count("=")
    return len(encoded_image) * 3 // 4 - padding
