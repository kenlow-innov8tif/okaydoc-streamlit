import requests
import streamlit as st
import io
import base64

def submit_okayid_api(edited_front, edited_back, journey_id, api_params, base_url=None):
    # Map JPG to JPEG for PIL compatibility
    format_map = {"JPG": "JPEG", "PNG": "PNG"}
    img_format = api_params.get('imageFormat', 'JPEG').upper()
    img_format = format_map.get(img_format, img_format)
    # Convert RGBA/LA/P to RGB for JPEG
    if img_format == "JPEG":
        if edited_front.mode in ("RGBA", "LA", "P"):
            edited_front = edited_front.convert("RGB")
        if edited_back.mode in ("RGBA", "LA", "P"):
            edited_back = edited_back.convert("RGB")
    buf_front = io.BytesIO()
    edited_front.save(buf_front, format=img_format)
    front_b64 = base64.b64encode(buf_front.getvalue()).decode("utf-8")
    buf_back = io.BytesIO()
    edited_back.save(buf_back, format=img_format)
    back_b64 = base64.b64encode(buf_back.getvalue()).decode("utf-8")
    payload = {
        "journeyId": journey_id,
        "base64ImageString": front_b64,
        "backImage": back_b64,
        "imageFormat": api_params['imageFormat'],
        "imageEnabled": api_params['imageEnabled'],
        "faceImageEnabled": api_params['faceImageEnabled'],
        "cambodia": api_params['cambodia']
    }
    if base_url is None:
        base_url = "https://ekycportaldemo.innov8tif.com"
    api_endpoint = base_url.rstrip("/") + "/api/ekyc/okayid"
    st.info(f"Sending OkayID API request to {api_endpoint} ...")
    response = requests.post(api_endpoint, json=payload)
    return response
