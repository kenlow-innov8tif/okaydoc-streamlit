import io
import unittest

from PIL import Image

from utils.image_uploads import load_uploaded_image, reset_edits_for_new_upload


def create_png_bytes(color):
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color).save(buffer, format="PNG")
    return buffer.getvalue()


class ImageUploadsTests(unittest.TestCase):
    def test_load_uploaded_image_returns_image_for_valid_upload(self):
        image = load_uploaded_image(create_png_bytes("red"))

        self.assertIsNotNone(image)
        self.assertEqual(image.size, (2, 2))

    def test_load_uploaded_image_returns_none_for_invalid_upload(self):
        self.assertIsNone(load_uploaded_image(b"not an image"))

    def test_new_upload_resets_existing_edit_values(self):
        state = {
            "front_brightness": 1.5,
            "front_brightness_slider": 1.5,
            "front_crop_enabled": True,
        }

        reset_edits_for_new_upload(state, "front", create_png_bytes("red"))

        self.assertEqual(state["front_brightness"], 1.0)
        self.assertEqual(state["front_brightness_slider"], 1.0)
        self.assertFalse(state["front_crop_enabled"])

    def test_same_upload_keeps_current_edit_values(self):
        image_bytes = create_png_bytes("red")
        state = {}
        reset_edits_for_new_upload(state, "front", image_bytes)
        state["front_brightness"] = 1.5
        state["front_brightness_slider"] = 1.5

        reset_edits_for_new_upload(state, "front", image_bytes)

        self.assertEqual(state["front_brightness"], 1.5)
        self.assertEqual(state["front_brightness_slider"], 1.5)

    def test_replaced_upload_resets_current_edit_values(self):
        state = {}
        reset_edits_for_new_upload(state, "front", create_png_bytes("red"))
        state["front_contrast"] = 1.5
        state["front_contrast_slider"] = 1.5

        reset_edits_for_new_upload(state, "front", create_png_bytes("blue"))

        self.assertEqual(state["front_contrast"], 1.0)
        self.assertEqual(state["front_contrast_slider"], 1.0)
