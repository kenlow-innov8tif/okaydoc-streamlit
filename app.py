import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import io
import base64
import requests

# Set page config for a wider layout
st.set_page_config(layout="wide", page_title="Image Editor & API Submitter")

st.title("Image Editor and OkayDoc Submitter")

# --- Sidebar for Journey ID and Reset ---
st.sidebar.header("Settings")
journey_id = st.sidebar.text_input("Enter Journey ID", "")

# Reset button
if st.sidebar.button("Reset Edits"):
    # Clear the session state variables related to image editing
    if 'brightness' in st.session_state:
        del st.session_state['brightness']
    if 'contrast' in st.session_state:
        del st.session_state['contrast']
    if 'crop_margin' in st.session_state:
        del st.session_state['crop_margin']
    # If the file uploader widget state needs to be reset,
    # Streamlit doesn't have a direct way to reset it programmatically without rerunning.
    # The simplest way for a user to "reset" the uploaded image is to re-upload.
    st.success("Image edit parameters have been reset!")
    st.rerun() # Rerun to apply resets

# --- Main Content Area ---
uploaded_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

original_image = None
if uploaded_file is not None:
    # Read image as bytes
    image_bytes = uploaded_file.getvalue()
    original_image = Image.open(io.BytesIO(image_bytes))

    st.subheader("Edit Image Parameters")

    # Create two columns: left for sliders, right for preview
    col1, col2 = st.columns([1, 1])

    with col1:
        # Use local variables for slider values to avoid Streamlit session state update issues
        brightness = st.session_state.get('brightness', 1.0)
        contrast = st.session_state.get('contrast', 1.0)
        crop_margin = st.session_state.get('crop_margin', 0)

        # Sliders for editing (more granular)
        brightness = st.slider(
            "Brightness", 0.0, 3.0, float(brightness), 0.01, format="%.2f"
        )
        contrast = st.slider(
            "Contrast", 0.0, 3.0, float(contrast), 0.01, format="%.2f"
        )

        st.markdown("---")
        st.write("Crop Margin (Negative: crop in, Positive: zoom out)")

        max_crop = min(original_image.width, original_image.height) // 2
        min_crop = -max_crop
        crop_margin = st.slider(
            "Crop/Zoom All Sides", min_crop, max_crop, int(crop_margin), 1
        )

        # Update session state only after all sliders
        st.session_state['brightness'] = brightness
        st.session_state['contrast'] = contrast
        st.session_state['crop_margin'] = crop_margin

    # Apply edits in real time as sliders are adjusted
    edited_image = original_image.copy()

    # Apply brightness
    enhancer = ImageEnhance.Brightness(edited_image)
    edited_image = enhancer.enhance(brightness)

    # Apply contrast
    enhancer = ImageEnhance.Contrast(edited_image)
    edited_image = enhancer.enhance(contrast)

    # Apply cropping/zooming
    width, height = edited_image.size
    margin = crop_margin
    left = margin
    top = margin
    right = width - margin
    bottom = height - margin

    # Ensure crop box is valid and does not exceed image bounds
    if left < right and top < bottom and left >= 0 and top >= 0 and right <= width and bottom <= height:
        edited_image = edited_image.crop((left, top, right, bottom))
    elif margin < 0:
        # For negative margin (zoom out), add border
        border = abs(margin)
        edited_image = ImageOps.expand(edited_image, border=border, fill=(0,0,0))
    else:
        st.warning("Invalid crop/zoom margin. Please adjust to ensure valid image dimensions.")
        edited_image = original_image # Revert to original if crop is invalid

    with col2:
        st.subheader("Image Preview")
        st.image(edited_image, caption="Edited Image Preview", use_column_width=True)

    # --- Submit to API ---
    if st.button("Submit Edited Image to API"):
        if journey_id == "":
            st.error("Please enter a Journey ID in the sidebar before submitting.")
        else:
            try:
                # Convert edited image to Base64
                buffered = io.BytesIO()
                # Save as JPEG for better compression, adjust quality if needed
                edited_image.save(buffered, format="JPEG", quality=85)
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

                # Construct the JSON payload
                payload = {
                    "journeyId": journey_id,
                    "type": "nonpassport",
                    "idImageBase64Image": img_str,
                    "livenessFaceBase64Image": "", # As per requirement, leaving empty
                    "version": "7",
                    "docType": "mykad",
                    "landmarkCheck": "true",
                    "fontCheck": "true",
                    "microprintCheck": "true",
                    "photoSubstitutionCheck": "true",
                    "icTypeCheck": "true",
                    "colorMode": "true",
                    "hologram": "true",
                    "screenDetection": "true",
                    "ghostPhotoColorDetection": "true",
                    "idBlurDetection": "true",
                    "idBrightnessDetection": "true",
                    "faceBrightnessDetection": "true",
                    "contentSubstitution": "true"
                }

                api_endpoint = "https://ekycportaldemo.innov8tif.com/api/ekyc/okaydoc"

                st.info("Sending request to API...")
                # Make the POST request
                response = requests.post(api_endpoint, json=payload)

                st.subheader("API Response")
                if response.status_code == 200:
                    st.success("Image successfully submitted!")
                    st.json(response.json()) # Display JSON response
                else:
                    st.error(f"API request failed with status code: {response.status_code}")
                    st.json(response.json()) # Display error JSON response if available
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e) # Display full exception traceback for debugging

else:
    st.info("Please upload an image to start editing.")

