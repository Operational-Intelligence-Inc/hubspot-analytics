import streamlit as st

home_page = st.Page("pages/0_Home.py", title="Home", icon="🏠")
init_page = st.Page("pages/1_Initialization.py", title="Initialization", icon="🔑")
cost_savings_page = st.Page("pages/2_Cost_Savings_Analysis.py", title="Cost Savings Analysis", icon="💰")

pg = st.navigation(
    [home_page,
    init_page,
    cost_savings_page]
)

pg.run()