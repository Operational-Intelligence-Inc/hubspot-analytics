import streamlit as st
from hubspot import HubSpot
from agno.models.openai import OpenAIChat
import openai
import os
import requests

# Set page configuration
st.set_page_config(page_title="Hubspot CRM Analysis", layout="centered")

# Initialize session state for API keys
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''
if 'hubspot_api_key' not in st.session_state:
    st.session_state['hubspot_api_key'] = ''

# Streamlit sidebar for API keys
with st.sidebar:
    st.title("API Keys Configuration")
    st.session_state['openai_api_key'] = st.text_input("Enter your OpenAI API Key", type="password").strip()
    st.session_state['hubspot_api_key'] = st.text_input("Enter your HubSpot Private App Key", type="password").strip()
    
    # Add info about API keys
    st.info("Please enter your API keys to access OpenAI and HubSpot services.")

# Validate API keys
if not st.session_state['openai_api_key'] or not st.session_state['hubspot_api_key']:
    st.error("Please enter both OpenAI and HubSpot API keys in the sidebar.")
    st.stop()

# Set the OpenAI API key from session state
os.environ["OPENAI_API_KEY"] = st.session_state['openai_api_key']


st.title("Hubspot CRM Initialization")

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
    st.write("### Account Details")
    st.json(account_details)
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
