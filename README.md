# HubSpot CRM Analytics - Multipage Streamlit App

A comprehensive analytics dashboard for HubSpot CRM data with AI-powered insights.

## 🚀 Features

### Pages Overview

1. **Home** (`streamlit_app.py`) - Main dashboard with overview and navigation
2. **Initialization** (`pages/1_Initialization.py`) - API key setup and validation
3. **Data Analysis** (`pages/2_Data_Analysis.py`) - AI-powered data analysis and insights
4. **Reports** (`pages/3_Reports.py`) - Generate and export reports
5. **Dashboard** (`pages/4_Dashboard.py`) - Real-time metrics and visualizations

### Key Features

- **Multipage Navigation**: Clean sidebar navigation between pages
- **API Integration**: HubSpot CRM and OpenAI API integration
- **Session State Management**: Persistent API keys across pages
- **Data Visualization**: Interactive charts and metrics
- **AI Insights**: OpenAI-powered data analysis
- **Report Generation**: Custom report builder with export options
- **Real-time Dashboard**: Live metrics and performance indicators

## 📋 Requirements

- Python 3.8+
- Streamlit
- HubSpot API Client
- OpenAI API
- Plotly (for charts)
- Pandas

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## 🔑 Setup

1. **HubSpot API Key**: Get your private app access token from HubSpot
2. **OpenAI API Key**: Get your API key from OpenAI
3. Navigate to the **Initialization** page to configure your API keys
4. Once configured, explore other pages for analytics and insights

## 📊 Pages Description

### Home Page
- Welcome screen with app overview
- API key status indicators
- Quick navigation to other pages
- Feature highlights

### Initialization Page
- API key configuration
- Connection validation
- Account details display
- Setup verification

### Data Analysis Page
- Contact analysis with demographics
- Deal pipeline analysis
- Company data insights
- AI-powered custom analysis

### Reports Page
- Pre-built report templates
- Custom report builder
- Multiple export formats (PDF, CSV, Excel)
- Date range filtering

### Dashboard Page
- Real-time KPIs
- Performance charts
- Deal pipeline visualization
- Recent activity feed
- Quick actions

## 🔧 Configuration

The app uses Streamlit's session state to persist API keys across pages. Each page includes:
- Sidebar with relevant controls
- API key validation
- Error handling
- Consistent UI/UX

## 📈 Usage

1. Start with the **Initialization** page to set up your API keys
2. Navigate to **Dashboard** for an overview of your CRM data
3. Use **Data Analysis** for detailed insights and AI-powered analysis
4. Generate reports using the **Reports** page
5. Export data and insights as needed

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is licensed under the MIT License.