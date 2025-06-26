import streamlit as st
from hubspot import HubSpot
from agno.models.openai import OpenAIChat
import openai
import os
import requests
from sidebar import render_sidebar
from streamlit_local_storage import LocalStorage
import json

st.title("Hubspot CRM Initialization")

# Use shared sidebar
with st.sidebar:
    render_sidebar() 

localS = LocalStorage()

# On page load, try to get both keys from a single dict in local storage
api_keys_str = localS.getItem("api_keys")
if api_keys_str is None:
    api_keys = {}
else:
    try:
        api_keys = json.loads(api_keys_str)
    except Exception:
        api_keys = {}
openai_api_key = api_keys.get('openai_api_key', st.session_state.get('openai_api_key', ''))
hubspot_api_key = api_keys.get('hubspot_api_key', st.session_state.get('hubspot_api_key', ''))

# API Key entry fields on the main page
st.write("#### Enter your API keys below:")
openai_api_key = st.text_input("OpenAI API Key", value=openai_api_key, type="password")
hubspot_api_key = st.text_input("HubSpot API Key", value=hubspot_api_key, type="password")

# Add notes for HubSpot API Key requirements
st.markdown("""
**Notes:**
- The API keys are stored in your browser's local storage and in the session state. They will persist across sessions in this browser.
- The HubSpot API key must be a **private app access token**.
- The private app must be granted the following scopes:
    - `crm.objects.users.read`
    - `automation.sequences.read`
    - `conversations.read`
    - `account-info.security.read`
    - `scheduler.meetings.meeting-link.read`
    - `crm.objects.companies.read`
    - `crm.objects.contacts.read`
""")

# Add submit button for API keys
submitted = st.button("Submit API Keys", type="primary")

# Only update session state and run validation after submit
if submitted:
    # Save both keys in a single dict in local storage (as JSON string)
    api_keys = {
        'openai_api_key': openai_api_key,
        'hubspot_api_key': hubspot_api_key
    }
    localS.setItem("api_keys", json.dumps(api_keys))
    # Save to session state
    st.session_state['openai_api_key'] = openai_api_key
    st.session_state['hubspot_api_key'] = hubspot_api_key

    # Validate API keys
    if not st.session_state['openai_api_key'] or not st.session_state['hubspot_api_key']:
        st.error("Please enter both OpenAI and HubSpot API keys above.")
        st.stop()

    # Set the OpenAI API key from session state
    os.environ["OPENAI_API_KEY"] = st.session_state['openai_api_key']

    # Initialize HubSpot client
    hubspot_client = HubSpot(access_token=st.session_state['hubspot_api_key'])

    # Get account details from HubSpot API
    url = "https://api.hubapi.com/account-info/v3/details"
    headers = {
        'accept': "application/json",
        'authorization': f"Bearer {st.session_state['hubspot_api_key']}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        account_details = response.json()
        # st.write("### Hubspot Account Details")
        # st.json(account_details)
        st.success("Hubspot API key is valid.")
        
        # Save uiDomain and portalId to session state
        st.session_state['ui_domain'] = account_details.get('uiDomain')
        st.session_state['portal_id'] = account_details.get('portalId')
        
        st.info(f"Saved to session: uiDomain = {st.session_state['ui_domain']}, portalId = {st.session_state['portal_id']}")
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching account details: {str(e)}")

    # Check and validate OpenAI API key
    # Function to check OpenAI API key validity
    def check_openai_api_key(api_key):
        client = openai.OpenAI(api_key=api_key)
        try:
            client.models.list()
        except openai.AuthenticationError:
            return False
        else:
            return True

    # Validate OpenAI API key
    try:
        if check_openai_api_key(st.session_state['openai_api_key']):
            st.success("OpenAI API key is valid.")
        else:
            st.error("Invalid OpenAI API key. Please check your API key and try again.")
            st.stop()
    except Exception as e:
        st.error(f"Error validating OpenAI API key: {str(e)}")
        st.stop()
else:
    # Do not run any validation or API calls before submit
    st.stop()

