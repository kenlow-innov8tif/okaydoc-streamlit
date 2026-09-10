"""Helpers for safely loading uploads and isolating image edit state."""

import hashlib
import io

from PIL import Image, UnidentifiedImageError

from utils.image_edit_state import reset_image_edit_state


def load_uploaded_image(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
        return image
    except (UnidentifiedImageError, OSError):
        return None


def reset_edits_for_new_upload(state, prefix, image_bytes):
    image_signature = hashlib.sha256(image_bytes).hexdigest()
    signature_key = f"{prefix}_image_signature"

    if state.get(signature_key) != image_signature:
        reset_image_edit_state(state, prefix)
        state[signature_key] = image_signature
