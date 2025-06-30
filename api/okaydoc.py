import requests
import streamlit as st
import io
import base64

def submit_okaydoc_api(edited_image, journey_id, api_params, base_url=None):
    buffered = io.BytesIO()
    edited_image.save(buffered, format="JPEG", quality=85)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    payload = {
        "journeyId": journey_id,
        "type": "nonpassport",
        "idImageBase64Image": img_str,
        "version": api_params['version'],
        "docType": api_params['docType'],
        "landmarkCheck": api_params['landmarkCheck'],
        "fontCheck": api_params['fontCheck'],
        "microprintCheck": api_params['microprintCheck'],
        "photoSubstitutionCheck": api_params['photoSubstitutionCheck'],
        "icTypeCheck": api_params['icTypeCheck'],
        "colorMode": api_params['colorMode'],
        "hologram": api_params['hologram'],
        "screenDetection": api_params['screenDetection'],
        "ghostPhotoColorDetection": api_params['ghostPhotoColorDetection'],
        "idBlurDetection": api_params['idBlurDetection'],
        "islamFieldTamperingDetection": api_params['islamFieldTamperingDetection'],
        "qualityCheckDetection": api_params['qualityCheckDetection']
    }
    if base_url is None:
        base_url = "https://ekycportaldemo.innov8tif.com"
    api_endpoint = base_url.rstrip("/") + "/api/ekyc/okaydoc"
    st.info(f"Sending request to API at {api_endpoint} ...")
    response = requests.post(api_endpoint, json=payload)
    return response
