import streamlit as st

# Sidebar with API key status
from sidebar import render_sidebar

# Set page configuration
st.set_page_config(
    page_title="Hubspot CRM Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for API keys
if 'openai_api_key' not in st.session_state:
    st.session_state['openai_api_key'] = ''
if 'hubspot_api_key' not in st.session_state:
    st.session_state['hubspot_api_key'] = ''

# Main page content
st.title("🚀 HubSpot CRM Analytics Dashboard")
st.markdown("---")

# Welcome section
st.header("Welcome to HubSpot CRM Analytics")
st.markdown("""
This application helps you analyze and optimize your HubSpot CRM usage with AI-powered insights and cost optimization tools.

### What you can do:
- **Initialize**: Set up your API keys and validate connections
- **Cost Savings Analysis**: Identify underutilized HubSpot seats and optimize costs
- **AI-Powered Insights**: Get intelligent recommendations for seat optimization (coming soon)
- **Detailed Reporting**: Export comprehensive analysis reports (coming soon)

### Getting Started:
1. Navigate to the **Initialization** page to set up your API keys
2. Once configured, explore the **Cost Savings Analysis** for optimization insights
""")

with st.sidebar:
    render_sidebar()

# Main content area with quick actions
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Quick Actions")
    if st.button("Go to Initialization", type="primary"):
        st.switch_page("pages/1_Initialization.py")
    
    st.markdown("""
    - Set up API keys
    - Validate connections
    - Check account details
    """)

with col2:
    st.subheader("💰 Cost Optimization Features")
    st.markdown("""
    - **High Priority Analysis**: Identify users inactive for 30+ days
    - **Medium Priority Review**: Check email and calendar connections
    - **Low Priority Review**: Analyze engagement patterns and meeting usage
    - **Export Reports**: Download detailed analysis as CSV
    """)
