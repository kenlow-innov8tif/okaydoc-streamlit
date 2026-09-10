import streamlit as st
from utils.api_parameters import build_okaydoc_api_params

def okayid_api_params_form():
    # Initialize session state for each parameter to ensure they persist
    if 'okayid_image_format' not in st.session_state:
        st.session_state['okayid_image_format'] = "JPG"
    if 'okayid_image_enabled' not in st.session_state:
        st.session_state['okayid_image_enabled'] = True
    if 'okayid_face_image_enabled' not in st.session_state:
        st.session_state['okayid_face_image_enabled'] = True
    if 'okayid_cambodia' not in st.session_state:
        st.session_state['okayid_cambodia'] = False

    with st.expander("API Request Parameters", expanded=True):
        st.subheader("API Request Parameters")
        
        # Use session state to manage radio button selection
        image_format = st.radio(
            "Image Format", ["JPG", "PNG"], 
            index=["JPG", "PNG"].index(st.session_state['okayid_image_format']), 
            key="okayid_image_format_radio"
        )
        image_enabled = st.radio(
            "Image Enabled", [True, False], 
            index=[True, False].index(st.session_state['okayid_image_enabled']), 
            key="okayid_image_enabled_radio"
        )
        face_image_enabled = st.radio(
            "Face Image Enabled", [True, False], 
            index=[True, False].index(st.session_state['okayid_face_image_enabled']), 
            key="okayid_face_image_enabled_radio"
        )
        cambodia = st.radio(
            "Cambodia", [True, False], 
            index=[True, False].index(st.session_state['okayid_cambodia']), 
            key="okayid_cambodia_radio"
        )

        # Update session state with the latest selections
        st.session_state['okayid_image_format'] = image_format
        st.session_state['okayid_image_enabled'] = image_enabled
        st.session_state['okayid_face_image_enabled'] = face_image_enabled
        st.session_state['okayid_cambodia'] = cambodia
        
        # Store the final parameters for API submission
        st.session_state['okayid_api_params'] = {
            'imageFormat': image_format,
            'imageEnabled': image_enabled,
            'faceImageEnabled': face_image_enabled,
            'cambodia': cambodia
        }

def okaydoc_api_params_form():
    with st.expander("API Request Parameters", expanded=False):
        st.subheader("API Request Parameters")
        doc_type = st.text_input("Document Type", value="mykad", key="doc_type_input")
        version = st.text_input("Version", value="7", key="version_input")
        landmark_check = st.radio("Landmark Check", ["true", "false"], index=0, key="landmarkCheck_radio")
        font_check = st.radio("Font Check", ["true", "false"], index=0, key="fontCheck_radio")
        microprint_check = st.radio("Microprint Check", ["true", "false"], index=0, key="microprintCheck_radio")
        photo_substitution_check = st.radio("Photo Substitution Check", ["true", "false"], index=0, key="photoSubstitutionCheck_radio")
        ic_type_check = st.radio("IC Type Check", ["true", "false"], index=0, key="icTypeCheck_radio")
        color_mode = st.radio("Color Mode", ["true", "false"], index=0, key="colorMode_radio")
        hologram = st.radio("Hologram", ["true", "false"], index=0, key="hologram_radio")
        screen_detection = st.radio("Screen Detection", ["true", "false"], index=0, key="screenDetection_radio")
        ghost_photo_color_detection = st.radio("Ghost Photo Color Detection", ["true", "false"], index=0, key="ghostPhotoColorDetection_radio")
        id_blur_detection = st.radio("ID Blur Detection", ["true", "false"], index=0, key="idBlurDetection_radio")
        islam_field_tampering_detection = st.radio("Islam Field Tampering Detection", ["true", "false"], index=0, key="islamFieldTamperingDetection_radio")
        quality_check_detection = st.radio("Quality Check Detection", ["true", "false"], index=0, key="qualityCheckDetection_radio")

        st.session_state['api_params'] = build_okaydoc_api_params(
            doc_type,
            version,
            landmark_check,
            font_check,
            microprint_check,
            photo_substitution_check,
            ic_type_check,
            color_mode,
            hologram,
            screen_detection,
            ghost_photo_color_detection,
            id_blur_detection,
            islam_field_tampering_detection,
            quality_check_detection,
        )
