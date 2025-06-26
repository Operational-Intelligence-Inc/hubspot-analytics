import requests
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def get_all_meeting_links(hubspot_api_key: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch all meeting links from HubSpot API with pagination support.
    
    Args:
        hubspot_api_key (str): HubSpot API access token
        limit (int): Number of results per page (max 100)
    
    Returns:
        List[Dict[str, Any]]: List of all meeting link objects
        
    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    all_meeting_links = []
    after = None
    
    while True:
        # Prepare the request
        url = "https://api.hubapi.com/scheduler/v3/meetings/meeting-links"
        headers = {
            'accept': "application/json",
            'authorization': f"Bearer {hubspot_api_key}"
        }
        
        # Build query parameters
        params = {"limit": str(limit)}
        if after:
            params["after"] = after
        
        try:
            # Make the API request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Add results to our collection
            if 'results' in data:
                all_meeting_links.extend(data['results'])
            
            # Check for pagination
            paging = data.get('paging', {})
            next_page = paging.get('next', {})
            
            if next_page and 'after' in next_page:
                after = next_page['after']
            else:
                # No more pages
                break
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching meeting links: {str(e)}")
            raise e
    
    return all_meeting_links


def get_meeting_links_with_progress(hubspot_api_key: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch all meeting links with progress indicator for Streamlit.
    
    Args:
        hubspot_api_key (str): HubSpot API access token
        limit (int): Number of results per page (max 100)
    
    Returns:
        List[Dict[str, Any]]: List of all meeting link objects
    """
    all_meeting_links = []
    after = None
    page_count = 0
    
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while True:
        page_count += 1
        status_text.text(f"Fetching page {page_count}...")
        
        # Prepare the request
        url = "https://api.hubapi.com/scheduler/v3/meetings/meeting-links"
        headers = {
            'accept': "application/json",
            'authorization': f"Bearer {hubspot_api_key}"
        }
        
        # Build query parameters
        params = {"limit": str(limit)}
        if after:
            params["after"] = after
        
        try:
            # Make the API request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Add results to our collection
            if 'results' in data:
                all_meeting_links.extend(data['results'])
                st.write(f"Retrieved {len(data['results'])} meeting links from page {page_count}")
            
            # Check for pagination
            paging = data.get('paging', {})
            next_page = paging.get('next', {})
            
            if next_page and 'after' in next_page:
                after = next_page['after']
                # Update progress (assuming we don't know total pages, just show we're working)
                progress_bar.progress(min(0.9, page_count * 0.1))
            else:
                # No more pages
                progress_bar.progress(1.0)
                status_text.text(f"Completed! Retrieved {len(all_meeting_links)} total meeting links from {page_count} pages.")
                break
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching meeting links on page {page_count}: {str(e)}")
            raise e
    
    return all_meeting_links


def get_all_engagements(hubspot_api_key: str, limit: int = 250, days_back: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch all engagements from HubSpot API with pagination support and date filtering.
    
    Args:
        hubspot_api_key (str): HubSpot API access token
        limit (int): Number of results per page (max 250)
        days_back (int): Number of days back to fetch engagements (default 30)
    
    Returns:
        List[Dict[str, Any]]: List of all engagement objects
        
    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    all_engagements = []
    offset = None
    cutoff_timestamp = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)
    
    while True:
        # Prepare the request
        url = "https://api.hubapi.com/engagements/v1/engagements/paged"
        headers = {
            'accept': "application/json",
            'authorization': f"Bearer {hubspot_api_key}"
        }
        
        # Build query parameters
        params = {"limit": str(limit)}
        if offset:
            params["offset"] = str(offset)
        
        try:
            # Make the API request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Add results to our collection
            if 'results' in data:
                # Filter engagements by creation date
                filtered_results = []
                for engagement in data['results']:
                    engagement_data = engagement.get('engagement', {})
                    created_at = engagement_data.get('createdAt', 0)
                    
                    # Stop if we've reached engagements older than our cutoff
                    if created_at < cutoff_timestamp:
                        return all_engagements
                    
                    filtered_results.append(engagement)
                
                all_engagements.extend(filtered_results)
            
            # Check for pagination
            has_more = data.get('hasMore', False)
            if has_more:
                offset = data.get('offset')
                if not offset:
                    break
            else:
                # No more pages
                break
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching engagements: {str(e)}")
            raise e
    
    return all_engagements


def get_engagements_with_progress(hubspot_api_key: str, limit: int = 250, days_back: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch all engagements with progress indicator for Streamlit.
    
    Args:
        hubspot_api_key (str): HubSpot API access token
        limit (int): Number of results per page (max 250)
        days_back (int): Number of days back to fetch engagements (default 30)
    
    Returns:
        List[Dict[str, Any]]: List of all engagement objects
    """
    all_engagements = []
    offset = None
    page_count = 0
    cutoff_timestamp = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)
    
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while True:
        page_count += 1
        status_text.text(f"Fetching engagements page {page_count}...")
        
        # Prepare the request
        url = "https://api.hubapi.com/engagements/v1/engagements/paged"
        headers = {
            'accept': "application/json",
            'authorization': f"Bearer {hubspot_api_key}"
        }
        
        # Build query parameters
        params = {"limit": str(limit)}
        if offset:
            params["offset"] = str(offset)
        
        try:
            # Make the API request
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Add results to our collection
            if 'results' in data:
                # Filter engagements by creation date
                filtered_results = []
                for engagement in data['results']:
                    engagement_data = engagement.get('engagement', {})
                    created_at = engagement_data.get('createdAt', 0)
                    
                    # Stop if we've reached engagements older than our cutoff
                    if created_at < cutoff_timestamp:
                        progress_bar.progress(1.0)
                        status_text.text(f"Completed! Retrieved {len(all_engagements)} total engagements from {page_count} pages (stopped at {days_back} days back).")
                        return all_engagements
                    
                    filtered_results.append(engagement)
                
                all_engagements.extend(filtered_results)
                st.write(f"Retrieved {len(filtered_results)} engagements from page {page_count}")
            
            # Check for pagination
            has_more = data.get('hasMore', False)
            if has_more:
                offset = data.get('offset')
                if not offset:
                    break
                # Update progress (assuming we don't know total pages, just show we're working)
                progress_bar.progress(min(0.9, page_count * 0.1))
            else:
                # No more pages
                progress_bar.progress(1.0)
                status_text.text(f"Completed! Retrieved {len(all_engagements)} total engagements from {page_count} pages.")
                break
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching engagements on page {page_count}: {str(e)}")
            raise e
    
    return all_engagements

