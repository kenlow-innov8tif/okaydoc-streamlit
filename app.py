import streamlit as st
from PIL import Image
import io
from components.image_edit import image_edit_tools
from components.api_forms import okayid_api_params_form, okaydoc_api_params_form
from api.journey import get_journey_id
import requests
import base64

# Set page config for a wider layout and light theme
st.set_page_config(
    layout="wide",
    page_title="Image Editor & API Submitter",
    initial_sidebar_state="auto"
)

# Inject CSS to force light mode and dark sidebar, but do NOT override radio button styles
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #23242a !important;
        color: #f5f5f5 !important;
    }
    .stButton>button, .st-expanderHeader, .stTextInput label, .stTextInput div, .stTextInput input, .stSidebar, .stSidebarContent {
        color: #f5f5f5 !important;
    }
    .st-bb, .st-bc, .st-bd, .st-be, .st-bf, .st-bg, .st-bh, .st-bi, .st-bj, .st-bk, .st-bl, .st-bm, .st-bn, .st-bo, .st-bp, .st-bq, .st-br, .st-bs, .st-bt, .st-bu, .st-bv, .st-bw, .st-bx, .st-by, .st-bz {
        background-color: #23242a !important;
    }
    .st-expanderHeader {
        background-color: #23242a !important;
        color: #f5f5f5 !important;
    }
    .stTextInput>div>input {
        background-color: #23242a !important;
        color: #f5f5f5 !important;
    }
    .stSidebar, .stSidebarContent {
        background-color: #1a1b1f !important;
        color: #f5f5f5 !important;
    }
    div[data-testid="stJson"] {
        overflow-x: auto;
    }
    div[data-testid="stJson"] * {
        white-space: pre !important;
        overflow-wrap: normal !important;
        word-break: normal !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar for Journey ID and Reset ---
st.sidebar.header("Settings")

# --- Environment Toggle ---
if 'environment' not in st.session_state:
    st.session_state['environment'] = 'DEMO'
# Use a checkbox instead of a toggle to avoid compatibility issues across browsers
env_checkbox = st.sidebar.checkbox('Production Environment', value=(st.session_state['environment'] == 'PRODUCTION'), key='env_toggle')
st.session_state['environment'] = 'PRODUCTION' if env_checkbox else 'DEMO'

# Set base URL based on environment
def get_base_url():
    if st.session_state.get('environment', 'DEMO') == 'PRODUCTION':
        return 'https://ekycportal.innov8tif.com'
    else:
        return 'https://ekycportaldemo.innov8tif.com'

# --- Sidebar Navigation ---
nav_options = ["OkayID Submitter", "OkayDoc (Non-Passport) Submitter", "OkayDoc Passport Submitter", "OkayFace Submitter", "OkayLive Submitter"]
nav_choice = st.sidebar.selectbox("Navigation", nav_options, key="nav_select")

# --- Journey ID Section (Always Visible) ---
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
            journey_api = get_base_url() + "/api/ekyc/journeyid"
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

def encode_image_base64(original_bytes, edited_image, is_edited, image_format, **save_options):
    if not is_edited:
        return base64.b64encode(original_bytes).decode("utf-8"), "Original upload"

    buffered = io.BytesIO()
    edited_image.save(buffered, format=image_format, **save_options)
    return base64.b64encode(buffered.getvalue()).decode("utf-8"), "Edited image"

def show_base64_output(image_label, image_base64, source_label):
    st.caption(f"{image_label} source: {source_label}. Final 30 characters: `{image_base64[-30:]}`")
    with st.expander(f"View {image_label} Base64"):
        st.text_area(
            f"{image_label} Base64 ({source_label})",
            image_base64,
            height=300,
        )

def okayid_submitter_page():
    st.title("OkayID Submitter")
    st.markdown("Upload Front Image of ID")
    front_file = st.file_uploader("Upload Front Image", type=["png", "jpg", "jpeg"], key="okayid_front")
    st.markdown("Upload Back Image of ID")
    back_file = st.file_uploader("Upload Back Image", type=["png", "jpg", "jpeg"], key="okayid_back")
    
    okayid_api_params_form()

    edited_front = None
    edited_back = None
    front_image = None
    back_image = None
    is_front_edited = False
    is_back_edited = False
    icc_profile_front = None
    icc_profile_back = None

    if front_file is not None:
        front_bytes = front_file.getvalue()
        front_image = Image.open(io.BytesIO(front_bytes))
        icc_profile_front = front_image.info.get('icc_profile')
        st.subheader("Edit Front Image Parameters")
        edited_front = image_edit_tools(front_image, "front")
        is_front_edited = (
            st.session_state.get('front_brightness', 1.0) != 1.0 or
            st.session_state.get('front_contrast', 1.0) != 1.0 or
            st.session_state.get('front_crop_margin', 0) != 0 or
            st.session_state.get('front_crop_enabled', False)
        )

    if back_file is not None:
        back_bytes = back_file.getvalue()
        back_image = Image.open(io.BytesIO(back_bytes))
        icc_profile_back = back_image.info.get('icc_profile')
        st.subheader("Edit Back Image Parameters")
        edited_back = image_edit_tools(back_image, "back")
        is_back_edited = (
            st.session_state.get('back_brightness', 1.0) != 1.0 or
            st.session_state.get('back_contrast', 1.0) != 1.0 or
            st.session_state.get('back_crop_margin', 0) != 0 or
            st.session_state.get('back_crop_enabled', False)
        )

    journey_id = get_journey_id()

    # Status text
    if front_file:
        if is_front_edited:
            st.info("Front Image Status: Sending edited image.")
        else:
            st.info("Front Image Status: Sending original image.")
    if back_file:
        if is_back_edited:
            st.info("Back Image Status: Sending edited image.")
        else:
            st.info("Back Image Status: Sending original image.")

    if front_file:
        image_to_submit_front = edited_front if is_front_edited else front_image
        if is_front_edited and image_to_submit_front.mode in ("RGBA", "LA", "P"):
            image_to_submit_front = image_to_submit_front.convert("RGB")
        front_b64, front_source_label = encode_image_base64(
            front_bytes,
            image_to_submit_front,
            is_front_edited,
            "JPEG",
            icc_profile=icc_profile_front,
        )
        show_base64_output("Front Image", front_b64, front_source_label)

    if back_file:
        image_to_submit_back = edited_back if is_back_edited else back_image
        if is_back_edited and image_to_submit_back.mode in ("RGBA", "LA", "P"):
            image_to_submit_back = image_to_submit_back.convert("RGB")
        back_b64, back_source_label = encode_image_base64(
            back_bytes,
            image_to_submit_back,
            is_back_edited,
            "JPEG",
            icc_profile=icc_profile_back,
        )
        show_base64_output("Back Image", back_b64, back_source_label)

    if st.button("Submit OkayID API Request"):
        if not journey_id:
            st.error("Please get a Journey ID in the sidebar before submitting.")
        elif front_file is None or back_file is None:
            st.error("Please upload both front and back images.")
        else:
            try:
                # Create payload from form and add images/journeyId
                payload = st.session_state.get('okayid_api_params', {})
                payload['journeyId'] = journey_id
                payload['base64ImageString'] = front_b64
                payload['backImage'] = back_b64
                
                api_url = get_base_url() + "/api/ekyc/okayid"
                resp = requests.post(api_url, json=payload)

                st.subheader("API Response")
                if resp.status_code == 200:
                    st.success("OkayID API request successful!")
                    st.json(resp.json())
                else:
                    st.error(f"API request failed with status code: {resp.status_code}")
                    try:
                        st.json(resp.json())
                    except Exception:
                        st.code(resp.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)

def okaydoc_submitter_page():
    st.title("OkayDoc Non-Passport Submitter")
    uploaded_file = st.file_uploader("Upload an ID Image", type=["png", "jpg", "jpeg"])
    okaydoc_api_params_form()
    original_image = None
    journey_id = get_journey_id()
    icc_profile = None

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        original_image = Image.open(io.BytesIO(image_bytes))
        icc_profile = original_image.info.get('icc_profile')
        st.subheader("Edit Image Parameters")
        edited_image = image_edit_tools(original_image, "doc")

        # Check if any edits were made
        is_edited = (
            st.session_state.get('doc_brightness', 1.0) != 1.0 or
            st.session_state.get('doc_contrast', 1.0) != 1.0 or
            st.session_state.get('doc_crop_margin', 0) != 0 or
            st.session_state.get('doc_crop_enabled', False)
        )

        image_to_submit = None
        if is_edited:
            st.info("Status: The edited image will be submitted.")
            image_to_submit = edited_image
        else:
            st.info("Status: The original image will be submitted without edits.")
            image_to_submit = original_image

        img_str, source_label = encode_image_base64(
            image_bytes,
            image_to_submit,
            is_edited,
            "PNG",
            optimize=True,
        )
        show_base64_output("ID Image", img_str, source_label)

        if st.button("Submit to OkayDoc API"):
            if not journey_id:
                st.error("Please get a Journey ID in the sidebar before submitting.")
            elif image_to_submit is None:
                st.error("Image not available for submission.") # Should not happen if file is uploaded
            else:
                try:
                    # Create payload
                    api_params = st.session_state.get('api_params', {})
                    payload = {
                        "journeyId": journey_id,
                        "type": "nonpassport",
                        "idImageBase64Image": img_str,
                    }
                    payload.update(api_params)

                    api_url = get_base_url() + "/api/ekyc/okaydoc"
                    st.info(f"Sending request to API at {api_url} ...")
                    response = requests.post(api_url, json=payload)
                    
                    st.subheader("API Response")
                    if response.status_code == 200:
                        st.success("Image successfully submitted!")
                        st.json(response.json())
                    else:
                        st.error(f"API request failed with status code: {response.status_code}")
                        st.json(response.json())
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.exception(e)

def okaydoc_passport_submitter_page():
    st.title("OkayDoc Passport Submitter")
    st.markdown("Upload Passport Images (Half Size and Full Size)")
    half_file = st.file_uploader("Upload Half Size Passport Image", type=["png", "jpg", "jpeg"], key="passport_half")
    full_file = st.file_uploader("Upload Full Size Passport Image (optional)", type=["png", "jpg", "jpeg"], key="passport_full")
    country = st.text_input("Country", value="OTHER", key="passport_country")

    edited_half = None
    edited_full = None
    half_image = None
    full_image = None
    is_half_edited = False
    is_full_edited = False
    icc_profile_half = None
    icc_profile_full = None
    
    if half_file is not None:
        half_bytes = half_file.getvalue()
        half_image = Image.open(io.BytesIO(half_bytes))
        icc_profile_half = half_image.info.get('icc_profile')
        st.subheader("Edit Half Size Image Parameters")
        edited_half = image_edit_tools(half_image, "passport_half")
        is_half_edited = (
            st.session_state.get('passport_half_brightness', 1.0) != 1.0 or
            st.session_state.get('passport_half_contrast', 1.0) != 1.0 or
            st.session_state.get('passport_half_crop_margin', 0) != 0 or
            st.session_state.get('passport_half_crop_enabled', False)
        )

    if full_file is not None:
        full_bytes = full_file.getvalue()
        full_image = Image.open(io.BytesIO(full_bytes))
        icc_profile_full = full_image.info.get('icc_profile')
        st.subheader("Edit Full Size Image Parameters")
        edited_full = image_edit_tools(full_image, "passport_full")
        is_full_edited = (
            st.session_state.get('passport_full_brightness', 1.0) != 1.0 or
            st.session_state.get('passport_full_contrast', 1.0) != 1.0 or
            st.session_state.get('passport_full_crop_margin', 0) != 0 or
            st.session_state.get('passport_full_crop_enabled', False)
        )

    journey_id = get_journey_id()

    # Status text
    if half_file:
        if is_half_edited:
            st.info("Half Size Image Status: Sending edited image.")
        else:
            st.info("Half Size Image Status: Sending original image.")
    if full_file:
        if is_full_edited:
            st.info("Full Size Image Status: Sending edited image.")
        else:
            st.info("Full Size Image Status: Sending original image.")

    if half_file:
        image_to_submit_half = edited_half if is_half_edited else half_image
        half_b64, half_source_label = encode_image_base64(
            half_bytes,
            image_to_submit_half,
            is_half_edited,
            "PNG",
            optimize=True,
        )
        show_base64_output("Half Size Image", half_b64, half_source_label)

    if full_file:
        image_to_submit_full = edited_full if is_full_edited else full_image
        full_b64, full_source_label = encode_image_base64(
            full_bytes,
            image_to_submit_full,
            is_full_edited,
            "PNG",
            optimize=True,
        )
        show_base64_output("Full Size Image", full_b64, full_source_label)

    if st.button("Submit Passport Images to OkayDoc API"):
        if not journey_id:
            st.error("Please get a Journey ID in the sidebar before submitting.")
        elif half_file is None:
            st.error("Please upload the half size image.")
        else:
            try:
                payload = {
                    "journeyId": journey_id,
                    "type": "passport",
                    "country": country,
                    "halfSizeImage": half_b64
                }

                if full_file is not None:
                    payload["fullSizeImage"] = full_b64

                api_url = get_base_url() + "/api/ekyc/okaydoc"
                resp = requests.post(api_url, json=payload)
                st.subheader("API Response")
                if resp.status_code == 200:
                    st.success("Passport images successfully submitted!")
                    st.json(resp.json())
                else:
                    st.error(f"API request failed with status code: {resp.status_code}")
                    try:
                        st.json(resp.json())
                    except Exception:
                        st.code(resp.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)

def okayface_submitter_page():
    st.title("OkayFace Submitter")
    st.markdown("Upload Face Images (ID Card and Best)")
    liveness = st.radio("Liveness Detection", options=["true", "false"], index=0, key="okayface_liveness")
    idcard_file = st.file_uploader("Upload ID Card Image", type=["png", "jpg", "jpeg"], key="okayface_idcard")
    best_file = st.file_uploader("Upload Best Face Image", type=["png", "jpg", "jpeg"], key="okayface_best")
    edited_idcard = None
    edited_best = None
    if idcard_file is not None:
        idcard_bytes = idcard_file.getvalue()
        idcard_image = Image.open(io.BytesIO(idcard_bytes))
        st.subheader("Edit ID Card Image Parameters")
        edited_idcard = image_edit_tools(idcard_image, "okayface_idcard")
    if best_file is not None:
        best_bytes = best_file.getvalue()
        best_image = Image.open(io.BytesIO(best_bytes))
        st.subheader("Edit Best Face Image Parameters")
        edited_best = image_edit_tools(best_image, "okayface_best")
    journey_id = get_journey_id()
    if st.button("Submit OkayFace API Request"):
        if not journey_id:
            st.error("Please get a Journey ID in the sidebar before submitting.")
        elif edited_idcard is None or edited_best is None:
            st.error("Please upload and edit both ID Card and Best Face images.")
        else:
            try:
                # Convert RGBA/LA/P to RGB for JPEG
                import tempfile
                import os
                idcard_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                best_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                try:
                    if edited_idcard.mode in ("RGBA", "LA", "P"):
                        edited_idcard = edited_idcard.convert("RGB")
                    edited_idcard.save(idcard_temp, format="JPEG")
                    idcard_temp.close()
                    if edited_best.mode in ("RGBA", "LA", "P"):
                        edited_best = edited_best.convert("RGB")
                    edited_best.save(best_temp, format="JPEG")
                    best_temp.close()
                    files = {
                        'imageIdCard': open(idcard_temp.name, 'rb'),
                        'imageBest': open(best_temp.name, 'rb')
                    }
                    data = {
                        'journeyId': journey_id,
                        'livenessDetection': liveness
                    }
                    api_url = get_base_url() + "/api/ekyc/okayface/v1-1"
                    resp = requests.post(api_url, data=data, files=files)
                    st.subheader("API Response")
                    if resp.status_code == 200:
                        st.success("OkayFace API request successful!")
                        st.json(resp.json())
                    else:
                        st.error(f"API request failed with status code: {resp.status_code}")
                        try:
                            st.json(resp.json())
                        except Exception:
                            st.code(resp.text)
                finally:
                    files['imageIdCard'].close()
                    files['imageBest'].close()
                    os.unlink(idcard_temp.name)
                    os.unlink(best_temp.name)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)

def okaylive_submitter_page():
    st.title("OkayLive Submitter")
    st.markdown("Upload Best Face Image for Liveness Check")
    best_file = st.file_uploader("Upload Best Face Image", type=["png", "jpg", "jpeg"], key="okaylive_best")
    edited_best = None
    if best_file is not None:
        best_bytes = best_file.getvalue()
        best_image = Image.open(io.BytesIO(best_bytes))
        st.subheader("Edit Best Face Image Parameters")
        edited_best = image_edit_tools(best_image, "okaylive_best")
    journey_id = get_journey_id()
    if st.button("Submit OkayLive API Request"):
        if not journey_id:
            st.error("Please get a Journey ID in the sidebar before submitting.")
        elif edited_best is None:
            st.error("Please upload and edit the Best Face image.")
        else:
            try:
                import tempfile
                import os
                best_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                try:
                    if edited_best.mode in ("RGBA", "LA", "P"):
                        edited_best = edited_best.convert("RGB")
                    edited_best.save(best_temp, format="JPEG")
                    best_temp.close()
                    files = {
                        'imageBest': open(best_temp.name, 'rb')
                    }
                    data = {
                        'journeyId': journey_id
                    }
                    api_url = get_base_url() + "/api/ekyc/okaylive"
                    resp = requests.post(api_url, data=data, files=files)
                    st.subheader("API Response")
                    if resp.status_code == 200:
                        st.success("OkayLive API request successful!")
                        st.json(resp.json())
                    else:
                        st.error(f"API request failed with status code: {resp.status_code}")
                        try:
                            st.json(resp.json())
                        except Exception:
                            st.code(resp.text)
                finally:
                    files['imageBest'].close()
                    os.unlink(best_temp.name)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)

# --- Main Navigation Logic ---
if nav_choice == "OkayID Submitter":
    okayid_submitter_page()
elif nav_choice == "OkayDoc (Non-Passport) Submitter":
    okaydoc_submitter_page()
elif nav_choice == "OkayDoc Passport Submitter":
    okaydoc_passport_submitter_page()
elif nav_choice == "OkayLive Submitter":
    okaylive_submitter_page()
else:
    okayface_submitter_page()

