import streamlit as st
from PIL import ImageEnhance, ImageOps
from streamlit_cropper import st_cropper

def image_edit_tools(image, prefix):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        brightness = st.session_state.get(f'{prefix}_brightness', 1.0)
        contrast = st.session_state.get(f'{prefix}_contrast', 1.0)
        crop_margin = st.session_state.get(f'{prefix}_crop_margin', 0)
        brightness = st.slider(f"Brightness ({prefix})", 0.0, 3.0, float(brightness), 0.01, format="%.2f", key=f"{prefix}_brightness_slider")
        contrast = st.slider(f"Contrast ({prefix})", 0.0, 3.0, float(contrast), 0.01, format="%.2f", key=f"{prefix}_contrast_slider")
        crop_margin = st.slider(f"Add Margin (px) ({prefix})", 0, 300, int(crop_margin), 1, key=f"{prefix}_margin_slider")
        st.session_state[f'{prefix}_brightness'] = brightness
        st.session_state[f'{prefix}_contrast'] = contrast
        st.session_state[f'{prefix}_crop_margin'] = crop_margin
        reset_btn = st.button(f"Reset Image Edit ({prefix})", key=f"reset_{prefix}_edit_btn")
        if reset_btn:
            st.session_state[f'{prefix}_brightness'] = 1.0
            st.session_state[f'{prefix}_contrast'] = 1.0
            st.session_state[f'{prefix}_crop_margin'] = 0
            st.rerun()
    with col2:
        st.subheader(f"Cropping Tool ({prefix})")
        cropper_aspect_ratio = None
        cropped_img = st_cropper(
            image,
            aspect_ratio=cropper_aspect_ratio,
            box_color='#27ae60',
            return_type='image',
            key=f'cropper_{prefix}',
            realtime_update=True
        )
    with col3:
        st.subheader(f"Final Result Preview ({prefix})")
        preview_img = cropped_img.copy()
        preview_img = ImageEnhance.Brightness(preview_img).enhance(st.session_state.get(f'{prefix}_brightness', 1.0))
        preview_img = ImageEnhance.Contrast(preview_img).enhance(st.session_state.get(f'{prefix}_contrast', 1.0))
        margin = st.session_state.get(f'{prefix}_crop_margin', 0)
        if margin > 0:
            preview_img = ImageOps.expand(preview_img, border=margin, fill=(0,0,0))
        st.image(preview_img, caption=f"Edited Image Preview ({prefix})", use_container_width=True)
    return preview_img
