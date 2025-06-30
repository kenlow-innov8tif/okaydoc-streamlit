import json
import streamlit as st

def get_journey_id():
    resp = st.session_state.get('journey_response')
    if isinstance(resp, dict) and 'journeyId' in resp:
        return resp['journeyId']
    elif isinstance(resp, str):
        try:
            return json.loads(resp).get('journeyId')
        except Exception:
            return None
    return None
