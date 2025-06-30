import streamlit as st
from PIL import Image, ImageEnhance, ImageOps
import io
import base64
import requests
from streamlit_cropper import st_cropper

# Set page config for a wider layout
st.set_page_config(layout="wide", page_title="Image Editor & API Submitter")

st.title("Image Editor and OkayDoc Submitter")

# --- Sidebar for Journey ID and Reset ---
st.sidebar.header("Settings")

# Make sidebar always visible (Streamlit sidebar is fixed by default and cannot be collapsed unless user clicks, so no code needed)

# --- Journey ID Submission Form ---
with st.sidebar.form(key="journey_id_form", clear_on_submit=False):
    st.markdown("**Get Journey ID**")
    username = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")
    submit_journey = st.form_submit_button("Submit for Journey ID")

# Persistent storage for journey response
if 'journey_response' not in st.session_state:
    st.session_state['journey_response'] = None

if submit_journey:
    if username and password:
        try:
            journey_payload = {"username": username, "password": password}
            journey_api = "https://ekycportaldemo.innov8tif.com/api/ekyc/journeyid"
            resp = requests.post(journey_api, json=journey_payload)
            if resp.status_code == 200:
                st.session_state['journey_response'] = resp.json()
                st.sidebar.success("Journey ID retrieved!")
            else:
                st.session_state['journey_response'] = resp.text
                st.sidebar.error(f"Failed: {resp.status_code}")
        except Exception as e:
            st.session_state['journey_response'] = str(e)
            st.sidebar.error(f"Error: {e}")
    else:
        st.sidebar.warning("Please enter both username and password.")

# Show journey response persistently in sidebar
if st.session_state['journey_response']:
    journey_id_value = None
    resp = st.session_state['journey_response']
    if isinstance(resp, dict) and 'journeyId' in resp:
        journey_id_value = resp['journeyId']
    elif isinstance(resp, str):
        import json
        try:
            resp_json = json.loads(resp)
            journey_id_value = resp_json.get('journeyId', None)
        except Exception:
            journey_id_value = None
    st.sidebar.markdown("**Journey ID Response**")
    if journey_id_value:
        st.sidebar.code(journey_id_value, language='text')
        st.sidebar.button("Copy to Clipboard", on_click=lambda: st.session_state.update({'_clipboard': journey_id_value}), key="copy_journey_id_btn")
    else:
        st.sidebar.code(resp, language='json')

# --- Main Content Area ---
uploaded_file = st.file_uploader("Upload an ID Image", type=["png", "jpg", "jpeg"])

original_image = None
# Use journey_id from session state if available
journey_id = None
if st.session_state.get('journey_response'):
    # Try to extract journeyId from the response if it's a dict
    resp = st.session_state['journey_response']
    if isinstance(resp, dict) and 'journeyId' in resp:
        journey_id = resp['journeyId']
    elif isinstance(resp, str):
        # Try to parse as JSON string
        import json
        try:
            resp_json = json.loads(resp)
            journey_id = resp_json.get('journeyId', None)
        except Exception:
            journey_id = None

# Collapsible container for API Request Parameters, above Edit Image Parameters
with st.expander("API Request Parameters", expanded=False):
    with st.form(key="api_params_form", clear_on_submit=False):
        st.subheader("API Request Parameters")
        # String fields
        doc_type = st.text_input("Document Type", value="mykad", key="doc_type_input")
        version = st.text_input("Version", value="7", key="version_input")
        # Boolean fields as radio buttons
        landmarkCheck = st.radio("Landmark Check", ["true", "false"], index=0, key="landmarkCheck_radio")
        fontCheck = st.radio("Font Check", ["true", "false"], index=0, key="fontCheck_radio")
        microprintCheck = st.radio("Microprint Check", ["true", "false"], index=0, key="microprintCheck_radio")
        photoSubstitutionCheck = st.radio("Photo Substitution Check", ["true", "false"], index=0, key="photoSubstitutionCheck_radio")
        icTypeCheck = st.radio("IC Type Check", ["true", "false"], index=0, key="icTypeCheck_radio")
        colorMode = st.radio("Color Mode", ["true", "false"], index=0, key="colorMode_radio")
        hologram = st.radio("Hologram", ["true", "false"], index=0, key="hologram_radio")
        screenDetection = st.radio("Screen Detection", ["true", "false"], index=0, key="screenDetection_radio")
        ghostPhotoColorDetection = st.radio("Ghost Photo Color Detection", ["true", "false"], index=0, key="ghostPhotoColorDetection_radio")
        idBlurDetection = st.radio("ID Blur Detection", ["true", "false"], index=0, key="idBlurDetection_radio")
        islamFieldTamperingDetection = st.radio("Islam Field Tampering Detection", ["true", "false"], index=0, key="islamFieldTamperingDetection_radio")
        qualityCheckDetection = st.radio("Quality Check Detection", ["true", "false"], index=0, key="qualityCheckDetection_radio")
        submit_api_params = st.form_submit_button("Save API Parameters")

    # Store API params in session state for use in request
    if submit_api_params or 'api_params' not in st.session_state:
        st.session_state['api_params'] = {
            'docType': doc_type,
            'version': version,
            'landmarkCheck': landmarkCheck,
            'fontCheck': fontCheck,
            'microprintCheck': microprintCheck,
            'photoSubstitutionCheck': photoSubstitutionCheck,
            'icTypeCheck': icTypeCheck,
            'colorMode': colorMode,
            'hologram': hologram,
            'screenDetection': screenDetection,
            'ghostPhotoColorDetection': ghostPhotoColorDetection,
            'idBlurDetection': idBlurDetection,
            'islamFieldTamperingDetection': islamFieldTamperingDetection,
            'qualityCheckDetection': qualityCheckDetection
        }

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

        # Add Reset Image Edit button below the sliders
        reset_image_edit = st.button("Reset Image Edit", key="reset_image_edit_btn")
        if reset_image_edit:
            st.session_state['brightness'] = 1.0
            st.session_state['contrast'] = 1.0
            st.session_state['crop_margin'] = 0
            st.rerun()

    with col2:
        st.subheader("Image Preview")
        # Interactive cropping with streamlit-cropper
        cropper_aspect_ratio = None  # Set to None for free aspect, or e.g. (1, 1) for square
        cropped_img = st_cropper(
            original_image,
            aspect_ratio=cropper_aspect_ratio,
            box_color='#27ae60',
            return_type='image',
            key='cropper',
        )
        # Apply brightness and contrast to the cropped image before showing preview
        preview_img = cropped_img.copy()
        preview_img = ImageEnhance.Brightness(preview_img).enhance(st.session_state.get('brightness', 1.0))
        preview_img = ImageEnhance.Contrast(preview_img).enhance(st.session_state.get('contrast', 1.0))
        st.image(preview_img, caption="Edited Image Preview", use_container_width=True)

    # Use preview_img for further processing and API submission
    edited_image = preview_img

    # --- Submit to API ---
    if st.button("Submit Edited Image to API"):
        if not journey_id:
            st.error("Please get a Journey ID in the sidebar before submitting.")
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
                    "version": st.session_state['api_params']['version'],
                    "docType": st.session_state['api_params']['docType'],
                    "landmarkCheck": st.session_state['api_params']['landmarkCheck'],
                    "fontCheck": st.session_state['api_params']['fontCheck'],
                    "microprintCheck": st.session_state['api_params']['microprintCheck'],
                    "photoSubstitutionCheck": st.session_state['api_params']['photoSubstitutionCheck'],
                    "icTypeCheck": st.session_state['api_params']['icTypeCheck'],
                    "colorMode": st.session_state['api_params']['colorMode'],
                    "hologram": st.session_state['api_params']['hologram'],
                    "screenDetection": st.session_state['api_params']['screenDetection'],
                    "ghostPhotoColorDetection": st.session_state['api_params']['ghostPhotoColorDetection'],
                    "idBlurDetection": st.session_state['api_params']['idBlurDetection'],
                    "islamFieldTamperingDetection": st.session_state['api_params']['islamFieldTamperingDetection'],
                    "qualityCheckDetection": st.session_state['api_params']['qualityCheckDetection']
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

