import unittest

from utils.image_edit_state import reset_image_edit_state


class ImageEditStateTests(unittest.TestCase):
    def test_reset_restores_edit_and_widget_defaults(self):
        state = {
            "front_brightness": 1.75,
            "front_brightness_slider": 1.75,
            "front_contrast": 0.5,
            "front_contrast_slider": 0.5,
            "front_crop_margin": 100,
            "front_margin_slider": 100,
            "front_crop_enabled": True,
            "cropper_front": {"left": 10},
        }

        reset_image_edit_state(state, "front")

        self.assertEqual(state["front_brightness"], 1.0)
        self.assertEqual(state["front_brightness_slider"], 1.0)
        self.assertEqual(state["front_contrast"], 1.0)
        self.assertEqual(state["front_contrast_slider"], 1.0)
        self.assertEqual(state["front_crop_margin"], 0)
        self.assertEqual(state["front_margin_slider"], 0)
        self.assertFalse(state["front_crop_enabled"])
        self.assertNotIn("cropper_front", state)
