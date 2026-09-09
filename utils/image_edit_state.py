"""State transitions for image editing controls."""


def reset_image_edit_state(state, prefix):
    state[f"{prefix}_brightness"] = 1.0
    state[f"{prefix}_brightness_slider"] = 1.0
    state[f"{prefix}_contrast"] = 1.0
    state[f"{prefix}_contrast_slider"] = 1.0
    state[f"{prefix}_crop_margin"] = 0
    state[f"{prefix}_margin_slider"] = 0
    state[f"{prefix}_crop_enabled"] = False
    state.pop(f"cropper_{prefix}", None)
