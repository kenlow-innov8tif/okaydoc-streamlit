import requests
import streamlit as st
import io
import base64

def submit_okayid_api(edited_front, edited_back, journey_id, api_params):
    buf_front = io.BytesIO()
    edited_front.save(buf_front, format=api_params['imageFormat'])
    front_b64 = base64.b64encode(buf_front.getvalue()).decode("utf-8")
    buf_back = io.BytesIO()
    edited_back.save(buf_back, format=api_params['imageFormat'])
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
    api_endpoint = "https://ekycportaldemo.innov8tif.com/api/ekyc/okayid"
    st.info("Sending OkayID API request...")
    response = requests.post(api_endpoint, json=payload)
    return response
