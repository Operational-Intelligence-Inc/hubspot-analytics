import streamlit as st
import pandas as pd
import plotly.express as px
from hubspot import HubSpot
import openai
import requests
from sidebar import render_sidebar
import datetime
from datetime import datetime, timedelta
import pytz
from utils import get_all_meeting_links, get_all_engagements

st.title("💰 Cost Savings Analysis")

st.markdown("""
### Purpose
This analysis helps identify **sales and service seat holders** who may be underutilizing their paid HubSpot seats, allowing you to optimize costs by:
- Reassigning seats to users who need them
- Removing unnecessary seats from your plan
- Converting users to free seats where appropriate

### How We Identify Underutilization
""")

# Create tabs for the three priority categories
tab1, tab2, tab3 = st.tabs(["🔴 High Priority Removal Targets", "🟡 Medium Priority Review", "🟢 Low Priority Review"])

with tab1:
    st.markdown("""
    These users are prime candidates for immediate seat removal:
    
    - **Users inactive for 30+ days**: Users who haven't logged into HubSpot for over a month
    - **Users who never logged in after being invited 30+ days ago**: Users who were invited but never accepted or used their account
    
    **Action**: Consider removing these seats immediately as they represent clear cost savings opportunities.
    """)

with tab2:
    st.markdown("""
    These users may need follow-up to determine if they should keep their seats:
    
    - **Users who have not connected their email account**: Users with sales/service seats who haven't connected their email integration
    - **Users who have not connected their calendar**: Users who haven't set up calendar integration for meetings
    
    **Action**: Reach out to these users to understand their needs and help them get properly set up, or consider seat removal if they don't need these features.
    """)

with tab3:
    st.markdown("""
    These users require deeper analysis and may need engagement data:
    
    - **Sales / Service seat holders with no recent engagements (30+ days)**: Users who haven't had recent customer interactions
    - **Sales seat holders with no meeting links**: Sales users who haven't created or used meeting scheduling
    - **Users with redundant sales + service seat combinations**: Users who may have both seat types unnecessarily
    
    **Action**: Review these cases individually. This analysis requires additional API calls and can be skipped for faster results.
    """)

st.markdown("""
**Notes:** 
- This analysis only includes users assigned to sales or service seats.
- Low priority review requires pull last 30 day engagement data from the engagement API and will be slower. Check the box below to skip this step.
""")

st.markdown("---")

# Use shared sidebar
with st.sidebar:
    render_sidebar()

# Check if API keys are configured
if not st.session_state.get('openai_api_key') or not st.session_state.get('hubspot_api_key'):
    st.error("Please configure your API keys in the Initialization page first.")
    st.stop()

# Initialize clients
hubspot_client = HubSpot(access_token=st.session_state['hubspot_api_key'])
openai_client = openai.OpenAI(api_key=st.session_state['openai_api_key'])

# Function to get all users with pagination
def get_all_users(hubspot_api_key):
    all_users = []
    url = "https://api.hubapi.com/crm/v3/objects/users"
    params = {
        "limit": 50,
        "properties": [
            "hs_last_activity_time",
            "hs_assigned_seats", 
            "hs_calendar_connection_status",
            "hs_connected_email_status",
            "hs_email",
            "hs_invite_accepted_time", 
            "hs_invite_email_status",
            "hs_invite_status",
            "hs_searchable_calculated_name",
            "hs_internal_user_id",
            "hubspot_owner_id",
            "hs_deactivated",
        ],
        "propertiesWithHistory": [
            "hs_invite_email_status",
            "hs_invite_status"
        ]
    }
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {hubspot_api_key}"
    }
    
    while True:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        all_users.extend(data["results"])
        
        # Check if there are more pages
        if "paging" in data and "next" in data["paging"]:
            params["after"] = data["paging"]["next"]["after"]
        else:
            break
            
    return all_users

# Function to clean User data into DataFrame
def clean_user_data(users):
    cleaned_data = []
    
    for user in users:
        # Start with the basic properties
        user_data = user["properties"].copy()
        
        # Handle propertiesWithHistory
        if "propertiesWithHistory" in user:
            history_data = user["propertiesWithHistory"]
            
            # Loop through all keys in propertiesWithHistory
            for key in history_data:
                if history_data[key]:  # If the array is not empty
                    # Take the first (latest) entry from the history
                    latest_entry = history_data[key][0]
                    user_data[f"{key}_timestamp"] = latest_entry["timestamp"]
                else:
                    # If the array is empty, set timestamp to null
                    user_data[f"{key}_timestamp"] = None
        
        cleaned_data.append(user_data)
    
    users_df = pd.DataFrame(cleaned_data)
    return users_df

# Function to identify underutilization
def identify_underutilization(users_df, skip_low_priority=False):
    """
    Identify underutilization patterns in the user dataframe.
    Adds columns to identify each type of underutilization.
    
    Args:
        users_df (pd.DataFrame): DataFrame containing user data
        skip_low_priority (bool): Whether to skip low priority review analysis
        
    Returns:
        pd.DataFrame: DataFrame with additional underutilization columns
    """
    df = users_df.copy()
    
    # Filter out deactivated users
    df = df[df['hs_deactivated'] != 'true']
    
    # Filter to only include users with sales or service seats
    df = df[df['hs_assigned_seats'].str.contains('sales|service', case=False, na=False)]
    
    # Convert timestamp columns to datetime
    timestamp_columns = [
        'hs_last_activity_time',
        'hs_invite_accepted_time',
        'hs_invite_email_status_timestamp',
        'hs_invite_status_timestamp'
    ]
    
    for col in timestamp_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Get current time in UTC for comparison (HubSpot timestamps are in UTC)
    utc = pytz.UTC
    current_time = datetime.now(utc)
    thirty_days_ago = current_time - timedelta(days=30)
    
    # Ensure all timestamps are timezone-aware (UTC)
    for col in timestamp_columns:
        if col in df.columns:
            # If timestamp is naive, localize to UTC, otherwise convert to UTC
            df[col] = df[col].apply(lambda x: utc.localize(x) if x is not None and x.tzinfo is None else x)
    
    # 🔴 HIGH PRIORITY REMOVAL TARGETS
    
    # 1. Users inactive for 30+ days
    df['inactive_30_plus_days'] = (
        (df['hs_last_activity_time'].notna()) & 
        (df['hs_last_activity_time'] < thirty_days_ago)
    )
    
    # 2. Users who never logged in after being invited 30+ days ago
    df['never_logged_in_after_invite'] = (
        (df['hs_invite_accepted_time'].isna()) & 
        (df['hs_invite_email_status_timestamp'].notna()) & 
        (df['hs_invite_email_status_timestamp'] < thirty_days_ago)
    )
    
    # 🟡 MEDIUM PRIORITY REVIEW
    
    # 3. Users who have not connected their email account
    df['email_not_connected'] = (
        (df['hs_connected_email_status'] != 'ENABLED') & 
        (df['hs_connected_email_status'].notna())
    )
    
    # 4. Users who have not connected their calendar
    df['calendar_not_connected'] = (
        (df['hs_calendar_connection_status'] != 'true') & 
        (df['hs_calendar_connection_status'].notna())
    )
    
    # 🟢 LOW PRIORITY REVIEW
    
    if skip_low_priority:
        # Skip low priority review - set all flags to False
        df['no_recent_engagements'] = False
        df['sales_no_meeting_links'] = False
        df['redundant_seat_combination'] = False
    else:
        # 5. Sales and Service seat holders with no recent engagements (30+ days)
        # Fetch engagements from the last 30 days and match to users
        engagement_status_text = st.empty()
        engagement_status_text.info("Fetching engagement data for low priority analysis...")
        try:
            engagements = get_all_engagements(st.session_state['hubspot_api_key'], days_back=30)
            
            if engagements:
                # Extract owner IDs from engagements
                users_with_engagements = set()
                for engagement in engagements:
                    engagement_data = engagement.get('engagement', {})
                    owner_id = engagement_data.get('ownerId')
                    if owner_id is not None and pd.notnull(owner_id) and str(owner_id).strip() != "":
                        users_with_engagements.add(str(owner_id))
                
                # Mark sales and service users without recent engagements
                df['no_recent_engagements'] = (
                    (df['hs_assigned_seats'].str.contains('sales|service', case=False, na=False)) &
                    (~df['hubspot_owner_id'].isin(users_with_engagements))
                )
                
                engagement_status_text.success(f"Successfully analyzed {len(engagements)} engagements from last 30 days. Found {len(users_with_engagements)} users with recent engagements.")
            else:
                engagement_status_text.warning("No engagements found in last 30 days. Setting all sales/service users as having no recent engagements.")
                df['no_recent_engagements'] = df['hs_assigned_seats'].str.contains('sales|service', case=False, na=False).astype(bool)
                
        except Exception as e:
            st.error(f"Error fetching engagements: {str(e)}")
            df['no_recent_engagements'] = pd.Series([False] * len(df), index=df.index)
        
        # 6. Sales seat holders with no meeting links
        # Fetch meeting links and join with users
        meeting_status_text = st.empty()
        meeting_status_text.info("Fetching meeting links data for low priority analysis...")
        try:
            meeting_links = get_all_meeting_links(st.session_state['hubspot_api_key'])
            
            if meeting_links:
                # Convert meeting links to DataFrame
                meeting_links_df = pd.DataFrame(meeting_links)
                
                # Create a set of user IDs who have meeting links
                users_with_meeting_links = set()
                for _, row in meeting_links_df.iterrows():
                    organizer_id = row.get('organizerUserId')
                    if organizer_id is not None and pd.notnull(organizer_id) and str(organizer_id).strip() != "":
                        users_with_meeting_links.add(organizer_id)
                
                # Mark sales users without meeting links
                df['sales_no_meeting_links'] = (
                    (df['hs_assigned_seats'].str.contains('sales', case=False, na=False)) &
                    (~df['hs_internal_user_id'].isin(users_with_meeting_links))
                )
                
                meeting_status_text.success(f"Successfully analyzed {len(meeting_links)} meeting links. Found {len(users_with_meeting_links)} users with meeting links.")
            else:
                meeting_status_text.warning("No meeting links found. Setting all sales users as having no meeting links.")
                df['sales_no_meeting_links'] = df['hs_assigned_seats'].str.contains('sales', case=False, na=False).astype(bool)
                
        except Exception as e:
            st.error(f"Error fetching meeting links: {str(e)}")
            df['sales_no_meeting_links'] = pd.Series([False] * len(df), index=df.index)
        
        # 7. Users with redundant sales + service seat combinations
        # Check if user has both sales and service seats
        df['redundant_seat_combination'] = (
            (df['hs_assigned_seats'].str.contains('sales', case=False, na=False)) &
            (df['hs_assigned_seats'].str.contains('service', case=False, na=False))
        )
    
    # Create priority columns
    df['high_priority_removal'] = df['inactive_30_plus_days'] | df['never_logged_in_after_invite']
    df['medium_priority_review'] = df['email_not_connected'] | df['calendar_not_connected']
    df['low_priority_review'] = (
        df['no_recent_engagements'] | 
        df['sales_no_meeting_links'] | 
        df['redundant_seat_combination']
    )
    
    # Create overall underutilization score
    df['underutilization_score'] = (
        df['high_priority_removal'].astype(int) * 3 +  # High priority = 3 points
        df['medium_priority_review'].astype(int) * 2 +  # Medium priority = 2 points
        df['low_priority_review'].astype(int) * 1  # Low priority = 1 point
    )
    
    # Create priority category
    def get_priority_category(row):
        if row['high_priority_removal']:
            return '🔴 High Priority'
        elif row['medium_priority_review']:
            return '🟡 Medium Priority'
        elif row['low_priority_review']:
            return '🟢 Low Priority'
        else:
            return '✅ No Issues'
    
    df['priority_category'] = df.apply(get_priority_category, axis=1)
    
    # Ensure all placeholder columns are boolean Series
    df['sales_no_meeting_links'] = df['sales_no_meeting_links'].astype(bool)
    df['no_recent_engagements'] = df['no_recent_engagements'].astype(bool)
    df['redundant_seat_combination'] = df['redundant_seat_combination'].astype(bool)
    
    return df

# Add checkbox to skip low priority review
skip_low_priority = st.checkbox(
    "Skip low priority review (faster analysis)", 
    help="Low priority review requires expensive API calls to engagement endpoints. Check this to skip this step for faster analysis."
)

# Add button to initiate analysis
analyze_button = st.button("Analyze Cost Savings", type="primary")

if analyze_button:
    with st.spinner("Analyzing cost savings..."):
        status_text = st.empty()
        status_text.info("Analysis in progress. This may take a few moments.")
        
        # Get all users only when button is pressed
        try:
            users = get_all_users(st.session_state['hubspot_api_key'])
            status_text.success(f"Successfully retrieved {len(users)} total users")
            
            # Convert to DataFrame for easier analysis using the clean function
            users_df = clean_user_data(users)
            
            # Show filtering information
            total_users = len(users_df)
            deactivated_users = (users_df['hs_deactivated'] == 'true').sum()
            users_with_sales_service_seats = users_df['hs_assigned_seats'].str.contains('sales|service', case=False, na=False).sum()
            
            st.info(f"""
            **Filtering Summary:**
            - Total users: {total_users}
            - Deactivated users (excluded): {deactivated_users}
            - Users with sales/service seats: {users_with_sales_service_seats}
            - Users analyzed: {users_with_sales_service_seats - deactivated_users}
            """)
            
            # Identify underutilization
            underutilized_users_df = identify_underutilization(users_df, skip_low_priority)
            
            # Create user links for all users
            ui_domain = st.session_state.get('ui_domain')
            portal_id = st.session_state.get('portal_id')
            
            if ui_domain and portal_id:
                underutilized_users_df['User Link'] = underutilized_users_df['hs_internal_user_id'].apply(
                    lambda x: f"https://{ui_domain}/settings/{portal_id}/users/user/{x}" if pd.notnull(x) else None
                )
            else:
                underutilized_users_df['User Link'] = None
            
            # Display summary statistics
            st.subheader("📊 Underutilization Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                high_priority_count = (underutilized_users_df['priority_category'] == '🔴 High Priority').sum()
                st.metric("🔴 High Priority", high_priority_count)
            
            with col2:
                medium_priority_count = (underutilized_users_df['priority_category'] == '🟡 Medium Priority').sum()
                st.metric("🟡 Medium Priority", medium_priority_count)
            
            with col3:
                low_priority_count = (underutilized_users_df['priority_category'] == '🟢 Low Priority').sum()
                st.metric("🟢 Low Priority", low_priority_count)
            
            with col4:
                no_issues_count = (underutilized_users_df['priority_category'] == '✅ No Issues').sum()
                st.metric("✅ No Issues", no_issues_count)
            
            # Display detailed breakdown
            st.subheader("🔍 Detailed Underutilization Analysis")
            
            # Create tabs for detailed analysis
            analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
                "🔴 High Priority", "🟡 Medium Priority", "🟢 Low Priority", "📋 Complete Analysis"
            ])
            
            # High Priority Users Tab
            with analysis_tab1:
                if high_priority_count > 0:
                    st.markdown("### 🔴 High Priority Removal Targets")
                    high_priority_users = underutilized_users_df[underutilized_users_df['priority_category'] == '🔴 High Priority']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        inactive_count = high_priority_users['inactive_30_plus_days'].sum()
                        st.metric("Inactive 30+ days", inactive_count)
                    
                    with col2:
                        never_logged_count = high_priority_users['never_logged_in_after_invite'].sum()
                        st.metric("Never logged in after invite", never_logged_count)
                    
                    # Prepare high priority display with improved formatting
                    high_priority_display = high_priority_users.copy()
                    
                    # Format dates to YYYY-MM-DD
                    if 'hs_last_activity_time' in high_priority_display.columns:
                        high_priority_display['Last Login Date'] = high_priority_display['hs_last_activity_time'].dt.strftime('%Y-%m-%d')
                    else:
                        high_priority_display['Last Login Date'] = None
                        
                    if 'hs_invite_accepted_time' in high_priority_display.columns:
                        high_priority_display['Invite Accept Date'] = high_priority_display['hs_invite_accepted_time'].dt.strftime('%Y-%m-%d')
                    else:
                        high_priority_display['Invite Accept Date'] = None
                    
                    # Select and rename columns for display
                    display_columns = {
                        'hs_searchable_calculated_name': 'Name',
                        'hs_email': 'Email',
                        'Last Login Date': 'Last Login Date',
                        'Invite Accept Date': 'Invite Accept Date',
                        'inactive_30_plus_days': '30+ Days Inactivity',
                        'never_logged_in_after_invite': '30+ Days Since Invite',
                        'User Link': 'User Link'
                    }
                    
                    # Filter to only include columns that exist
                    available_columns = {k: v for k, v in display_columns.items() if k in high_priority_display.columns}
                    high_priority_display = high_priority_display[list(available_columns.keys())].rename(columns=available_columns)
                    
                    # Display the table
                    st.dataframe(
                        high_priority_display, 
                        use_container_width=True,
                        column_config={
                            "User Link": st.column_config.LinkColumn(
                                display_text="User Link",
                                help="Click to open user profile in HubSpot",
                                max_chars=None,
                                validate="^https://.*"
                            )
                        }
                    )
                else:
                    st.info("✅ No high priority removal targets found.")
            
            # Medium Priority Users Tab
            with analysis_tab2:
                if medium_priority_count > 0:
                    st.markdown("### 🟡 Medium Priority Review")
                    medium_priority_users = underutilized_users_df[underutilized_users_df['priority_category'] == '🟡 Medium Priority']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        email_not_connected_count = medium_priority_users['email_not_connected'].sum()
                        st.metric("Email not connected", email_not_connected_count)
                    
                    with col2:
                        calendar_not_connected_count = medium_priority_users['calendar_not_connected'].sum()
                        st.metric("Calendar not connected", calendar_not_connected_count)
                    
                    # Prepare medium priority display with improved formatting
                    medium_priority_display = medium_priority_users.copy()
                    
                    # Select and rename columns for display
                    display_columns = {
                        'hs_searchable_calculated_name': 'Name',
                        'hs_email': 'Email',
                        'hs_connected_email_status': 'Email Status',
                        'hs_calendar_connection_status': 'Calendar Status',
                        'email_not_connected': 'Email Not Connected',
                        'calendar_not_connected': 'Calendar Not Connected',
                        'User Link': 'User Link'
                    }
                    
                    # Filter to only include columns that exist
                    available_columns = {k: v for k, v in display_columns.items() if k in medium_priority_display.columns}
                    medium_priority_display = medium_priority_display[list(available_columns.keys())].rename(columns=available_columns)
                    
                    # Display the table
                    st.dataframe(
                        medium_priority_display, 
                        use_container_width=True,
                        column_config={
                            "User Link": st.column_config.LinkColumn(
                                display_text="User Link",
                                help="Click to open user profile in HubSpot",
                                max_chars=None,
                                validate="^https://.*"
                            )
                        }
                    )
                else:
                    st.info("✅ No medium priority review targets found.")
            
            # Low Priority Users Tab
            with analysis_tab3:
                if low_priority_count > 0 and not skip_low_priority:
                    st.markdown("### 🟢 Low Priority Review")
                    low_priority_users = underutilized_users_df[underutilized_users_df['priority_category'] == '🟢 Low Priority']
                    
                    # Prepare low priority display with improved formatting
                    low_priority_display = low_priority_users.copy()
                    
                    # Select and rename columns for display
                    display_columns = {
                        'hs_searchable_calculated_name': 'Name',
                        'hs_email': 'Email',
                        'no_recent_engagements': 'No Recent Engagements',
                        'sales_no_meeting_links': 'No Meeting Links',
                        'redundant_seat_combination': 'Redundant Seat Combination',
                        'User Link': 'User Link'
                    }
                    
                    # Filter to only include columns that exist
                    available_columns = {k: v for k, v in display_columns.items() if k in low_priority_display.columns}
                    low_priority_display = low_priority_display[list(available_columns.keys())].rename(columns=available_columns)
                    
                    # Display the table
                    st.dataframe(
                        low_priority_display, 
                        use_container_width=True,
                        column_config={
                            "User Link": st.column_config.LinkColumn(
                                display_text="User Link",
                                help="Click to open user profile in HubSpot",
                                max_chars=None,
                                validate="^https://.*"
                            )
                        }
                    )
                elif skip_low_priority:
                    st.info("🟢 Low Priority Review was skipped for faster analysis. Uncheck the 'Skip low priority review' option to include this analysis.")
                else:
                    st.info("✅ No low priority review targets found.")
            
            # Complete Analysis Tab
            with analysis_tab4:
                st.markdown("### 📋 Complete Analysis Table")
                
                # Prepare complete analysis display with improved formatting
                complete_display = underutilized_users_df.copy()
                
                # Format dates to YYYY-MM-DD
                if 'hs_last_activity_time' in complete_display.columns:
                    complete_display['Last Login Date'] = complete_display['hs_last_activity_time'].dt.strftime('%Y-%m-%d')
                else:
                    complete_display['Last Login Date'] = None
                    
                if 'hs_invite_accepted_time' in complete_display.columns:
                    complete_display['Invite Accept Date'] = complete_display['hs_invite_accepted_time'].dt.strftime('%Y-%m-%d')
                else:
                    complete_display['Invite Accept Date'] = None
                
                # Select and rename columns for display - include all detailed columns
                display_columns = {
                    'hs_searchable_calculated_name': 'Name',
                    'hs_email': 'Email',
                    'priority_category': 'Priority Category',
                    'inactive_30_plus_days': '30+ Days Inactivity',
                    'never_logged_in_after_invite': '30+ Days Since Invite',
                    'email_not_connected': 'Email Not Connected',
                    'calendar_not_connected': 'Calendar Not Connected',
                    'no_recent_engagements': 'No Recent Engagements',
                    'sales_no_meeting_links': 'No Meeting Links',
                    'redundant_seat_combination': 'Redundant Seat Combination',
                    'User Link': 'User Link'
                }
                
                # Filter to only include columns that exist
                available_columns = {k: v for k, v in display_columns.items() if k in complete_display.columns}
                complete_display = complete_display[list(available_columns.keys())].rename(columns=available_columns)
                
                # Display the table
                st.dataframe(
                    complete_display, 
                    use_container_width=True,
                    column_config={
                        "User Link": st.column_config.LinkColumn(
                            display_text="User Link",
                            help="Click to open user profile in HubSpot",
                            max_chars=None,
                            validate="^https://.*"
                        )
                    }
                )
                
                # Download option
                csv = underutilized_users_df.to_csv(index=False)  # type: ignore
                st.download_button(
                    label="📥 Download Complete Analysis as CSV",
                    data=csv,
                    file_name=f"hubspot_cost_savings_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
