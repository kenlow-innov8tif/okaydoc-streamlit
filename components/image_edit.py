import streamlit as st
from PIL import ImageEnhance, ImageOps
from streamlit_cropper import st_cropper

def image_edit_tools(image, prefix):
    # Initialize session state for cropping if it doesn't exist
    if f'{prefix}_crop_enabled' not in st.session_state:
        st.session_state[f'{prefix}_crop_enabled'] = False

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

        # Conditionally show the 'Enable Cropping' button
        if not st.session_state.get(f'{prefix}_crop_enabled', False):
            if st.button(f"Enable Cropping ({prefix})", key=f"enable_crop_{prefix}"):
                st.session_state[f'{prefix}_crop_enabled'] = True
                st.rerun()

        reset_btn = st.button(f"Reset Image Edit ({prefix})", key=f"reset_{prefix}_edit_btn")
        if reset_btn:
            st.session_state[f'{prefix}_brightness'] = 1.0
            st.session_state[f'{prefix}_contrast'] = 1.0
            st.session_state[f'{prefix}_crop_margin'] = 0
            st.session_state[f'{prefix}_crop_enabled'] = False  # Reset cropping state
            st.rerun()

    # Determine the base image for processing (original or cropped)
    if st.session_state.get(f'{prefix}_crop_enabled', False):
        with col2:
            st.subheader(f"Cropping Tool ({prefix})")
            
            # Define a max width for the cropper's display to ensure it fits
            max_display_width = 400
            original_width, original_height = image.size
            
            if original_width > max_display_width:
                display_height = int(original_height * (max_display_width / original_width))
                display_image = image.resize((max_display_width, display_height))
                scale_factor = original_width / max_display_width
            else:
                display_image = image
                scale_factor = 1.0

            # Get the crop box from the user on the resized image
            box = st_cropper(
                display_image,
                return_type='box',
                box_color='#27ae60',
                key=f'cropper_{prefix}'
            )

            # Scale the crop box coordinates back to the original image size
            left = int(box['left'] * scale_factor)
            top = int(box['top'] * scale_factor)
            right = left + int(box['width'] * scale_factor)
            bottom = top + int(box['height'] * scale_factor)

            # Crop the original, full-resolution image
            processed_image = image.crop((left, top, right, bottom))
    else:
        processed_image = image.copy()
        with col2:
            st.subheader(f"Original Image ({prefix})")
            st.image(image, caption="Original (Uncropped)", use_container_width=True)

    with col3:
        st.subheader(f"Final Result Preview ({prefix})")
        # Apply enhancements to the processed_image
        preview_img = processed_image.copy()
        preview_img = ImageEnhance.Brightness(preview_img).enhance(st.session_state.get(f'{prefix}_brightness', 1.0))
        preview_img = ImageEnhance.Contrast(preview_img).enhance(st.session_state.get(f'{prefix}_contrast', 1.0))
        margin = st.session_state.get(f'{prefix}_crop_margin', 0)
        if margin > 0:
            preview_img = ImageOps.expand(preview_img, border=margin, fill=(0, 0, 0))
        st.image(preview_img, caption=f"Edited Image Preview ({prefix})", use_container_width=True)

    return preview_img
