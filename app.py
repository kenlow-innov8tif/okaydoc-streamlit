import streamlit as st
from PIL import Image
import io
from components.image_edit import image_edit_tools
from components.api_forms import okayid_api_params_form, okaydoc_api_params_form
from api.journey import get_journey_id
from api.okayid import submit_okayid_api
from api.okaydoc import submit_okaydoc_api
import requests

# Set page config for a wider layout and light theme
st.set_page_config(
    layout="wide",
    page_title="Image Editor & API Submitter",
    initial_sidebar_state="auto"
)

# Inject CSS to force light mode
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #23242a !important;
        color: #f5f5f5 !important;
    }
    .stButton>button, .stRadio label, .stRadio div, .stRadio span, .st-expanderHeader, .stTextInput label, .stTextInput div, .stTextInput input, .stSidebar, .stSidebarContent {
        color: #f5f5f5 !important;
    }
    .stRadio > div[role='radiogroup'] label {
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
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar for Journey ID and Reset ---
st.sidebar.header("Settings")

# Only create the journey ID form ONCE, outside of navigation logic
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

# --- Sidebar Navigation ---
nav_options = ["OkayID Submitter", "OkayDoc Submitter"]
if 'nav_page' not in st.session_state:
    st.session_state['nav_page'] = nav_options[0]
nav_choice = st.sidebar.radio("Navigation", nav_options, key="nav_radio")
st.session_state['nav_page'] = nav_choice

def okayid_submitter_page():
    st.title("OkayID Submitter")
    st.markdown("Upload Front Image of ID")
    front_file = st.file_uploader("Upload Front Image", type=["png", "jpg", "jpeg"], key="okayid_front")
    st.markdown("Upload Back Image of ID")
    back_file = st.file_uploader("Upload Back Image", type=["png", "jpg", "jpeg"], key="okayid_back")
    okayid_api_params_form()
    edited_front = None
    edited_back = None
    if front_file is not None:
        front_bytes = front_file.getvalue()
        front_image = Image.open(io.BytesIO(front_bytes))
        st.subheader("Edit Front Image Parameters")
        edited_front = image_edit_tools(front_image, "front")
    if back_file is not None:
        back_bytes = back_file.getvalue()
        back_image = Image.open(io.BytesIO(back_bytes))
        st.subheader("Edit Back Image Parameters")
        edited_back = image_edit_tools(back_image, "back")
    journey_id = get_journey_id()
    if st.button("Submit OkayID API Request"):
        if not journey_id:
            st.error("Please get a Journey ID in the sidebar before submitting.")
        elif edited_front is None or edited_back is None:
            st.error("Please upload and edit both front and back images.")
        else:
            try:
                response = submit_okayid_api(edited_front, edited_back, journey_id, st.session_state['okayid_api_params'])
                st.subheader("API Response")
                if response.status_code == 200:
                    st.success("OkayID API request successful!")
                    st.json(response.json())
                else:
                    st.error(f"API request failed with status code: {response.status_code}")
                    try:
                        st.json(response.json())
                    except Exception:
                        st.code(response.text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.exception(e)

def okaydoc_submitter_page():
    st.title("OkayDoc Submitter")
    uploaded_file = st.file_uploader("Upload an ID Image", type=["png", "jpg", "jpeg"])
    okaydoc_api_params_form()
    original_image = None
    journey_id = get_journey_id()
    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        original_image = Image.open(io.BytesIO(image_bytes))
        st.subheader("Edit Image Parameters")
        edited_image = image_edit_tools(original_image, "doc")
        if st.button("Submit Edited Image to API"):
            if not journey_id:
                st.error("Please get a Journey ID in the sidebar before submitting.")
            else:
                try:
                    response = submit_okaydoc_api(edited_image, journey_id, st.session_state['api_params'])
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

# --- Main Navigation Logic ---
if st.session_state['nav_page'] == "OkayID Submitter":
    okayid_submitter_page()
else:
    okaydoc_submitter_page()

