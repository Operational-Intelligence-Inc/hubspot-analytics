import streamlit as st

def render_sidebar():

    st.title("🔑 API Configuration Status")
    
    # Check if API keys are set
    openai_status = "✅ Configured" if st.session_state.get('openai_api_key') else "❌ Not Set"
    hubspot_status = "✅ Configured" if st.session_state.get('hubspot_api_key') else "❌ Not Set"
    
    st.write(f"**OpenAI API Key:** {openai_status}")
    st.write(f"**HubSpot API Key:** {hubspot_status}")
    
    if st.session_state.get('openai_api_key') and st.session_state.get('hubspot_api_key'):
        st.success("All API keys are configured!")
    else:
        st.warning("Please configure your API keys in the Initialization page.")
        if st.button("Go to Initialization", type="primary"):
            st.switch_page("pages/1_Initialization.py") 