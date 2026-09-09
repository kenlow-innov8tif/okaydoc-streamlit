import base64
import io
import unittest

from PIL import Image

from utils.image_encoding import encode_image_base64, get_base64_decoded_size


class EncodeImageBase64Tests(unittest.TestCase):
    def test_base64_size_metadata_does_not_require_decoding_payload(self):
        self.assertEqual(get_base64_decoded_size(""), 0)
        self.assertEqual(get_base64_decoded_size("YQ=="), 1)
        self.assertEqual(get_base64_decoded_size("YWI="), 2)
        self.assertEqual(get_base64_decoded_size("YWJj"), 3)

    def test_unedited_upload_preserves_original_bytes(self):
        original_bytes = b"original-upload-bytes\x00\xff"

        encoded_image, source = encode_image_base64(
            original_bytes,
            Image.new("RGB", (1, 1), "red"),
            is_edited=False,
            image_format="PNG",
        )

        self.assertEqual(base64.b64decode(encoded_image), original_bytes)
        self.assertEqual(source, "Original upload")

    def test_edited_image_is_serialized_as_jpeg(self):
        encoded_image, source = encode_image_base64(
            b"unused-original-bytes",
            Image.new("RGB", (2, 2), "red"),
            is_edited=True,
            image_format="JPEG",
        )

        image = Image.open(io.BytesIO(base64.b64decode(encoded_image)))

        self.assertEqual(image.format, "JPEG")
        self.assertEqual(source, "Edited image")

    def test_edited_image_is_serialized_as_png(self):
        encoded_image, source = encode_image_base64(
            b"unused-original-bytes",
            Image.new("RGBA", (2, 2), (255, 0, 0, 128)),
            is_edited=True,
            image_format="PNG",
            optimize=True,
        )

        image = Image.open(io.BytesIO(base64.b64decode(encoded_image)))

        self.assertEqual(image.format, "PNG")
        self.assertEqual(image.mode, "RGBA")
        self.assertEqual(source, "Edited image")
