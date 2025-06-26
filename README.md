# HubSpot CRM Cost Optimization - Streamlit App

A specialized analytics application for optimizing HubSpot CRM costs by identifying underutilized seats and providing AI-powered insights for cost savings.

## 🚀 Features

### Pages Overview

1. **Home** (`pages/0_Home.py`) - Welcome dashboard with overview and navigation
2. **Initialization** (`pages/1_Initialization.py`) - API key setup and validation
3. **Cost Savings Analysis** (`pages/2_Cost_Savings_Analysis.py`) - Comprehensive seat utilization analysis

### Key Features

- **Cost Optimization Focus**: Specialized analysis for identifying underutilized HubSpot seats
- **Multi-Priority Analysis**: Categorized recommendations (High, Medium, Low priority)
- **API Integration**: HubSpot CRM and OpenAI API integration
- **Session State Management**: Persistent API keys across pages with local storage
- **Data Visualization**: Interactive charts and metrics for seat utilization
- **Export Capabilities**: Download analysis results as CSV reports
- **Real-time Validation**: Live API key validation and connection testing

## 📋 Requirements

- Python 3.8+
- Streamlit
- HubSpot API Client
- OpenAI API
- Plotly (for charts)
- Pandas
- Streamlit Local Storage

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## 🔑 Setup

1. **HubSpot API Key**: Get your private app access token from HubSpot
   - Required scopes: `crm.objects.users.read`, `automation.sequences.read`, `conversations.read`, `account-info.security.read`, `scheduler.meetings.meeting-link.read`
2. **OpenAI API Key**: Get your API key from OpenAI
3. Navigate to the **Initialization** page to configure your API keys
4. Once configured, explore the **Cost Savings Analysis** for optimization insights

## 📊 Pages Description

### Home Page
- Welcome screen with app overview
- API key status indicators
- Quick navigation to other pages
- Feature highlights focused on cost optimization

### Initialization Page
- API key configuration with secure storage
- Connection validation for both HubSpot and OpenAI
- Account details display
- Setup verification with detailed scope requirements

### Cost Savings Analysis Page
- **High Priority Removal Targets**: Users inactive for 30+ days or never logged in
- **Medium Priority Review**: Users without email/calendar connections
- **Low Priority Review**: Users with no recent engagements or meeting links
- Interactive data tables with filtering
- Export functionality for analysis results
- Detailed recommendations for each user category

## 🔧 Configuration

The app uses Streamlit's session state and local storage to persist API keys across sessions. Each page includes:
- Shared sidebar with API key status
- Comprehensive error handling
- Consistent UI/UX design
- Secure API key storage

## 📈 Usage

1. Start with the **Initialization** page to set up your API keys
2. Navigate to **Cost Savings Analysis** for detailed seat utilization insights
3. Review users by priority category (High, Medium, Low)
4. Export analysis results for further review
5. Take action based on recommendations to optimize costs

## 🎯 Analysis Categories

### High Priority Removal Targets
- Users inactive for 30+ days
- Users who never logged in after being invited 30+ days ago
- **Action**: Consider immediate seat removal

### Medium Priority Review
- Users without email account connections
- Users without calendar connections
- **Action**: Follow up to understand needs or consider removal

### Low Priority Review
- Sales/Service seat holders with no recent engagements
- Sales seat holders with no meeting links
- Users with redundant seat combinations
- **Action**: Individual review with additional engagement data

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is licensed under the MIT License.