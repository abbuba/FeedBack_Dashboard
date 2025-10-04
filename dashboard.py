import streamlit as st
import requests

# Page Config & API URL
st.set_page_config(page_title="AgentSync Dashboard", layout="wide", page_icon="🚀")
API_URL = "https://ai-feedback-pj5y.onrender.com"

# --- Helper Functions ---
@st.cache_data(ttl=300)
def get_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

# --- Main Dashboard ---
st.title("🚀 AgentSync Leadership Dashboard")

companies = get_data("companies")

if not companies:
    st.error("Could not connect to the backend API. Please ensure the server is running.")
else:
    company_map = {comp['name']: comp['id'] for comp in companies}
    
    # --- 1. Main Company Selector ---
    selected_company_name = st.selectbox(
        "Select a Company to Analyze", 
        options=company_map.keys(),
        index=0 # Default to the first company
    )
    
    if selected_company_name:
        company_id = company_map[selected_company_name]
        st.header(f"Analysis for: {selected_company_name}")
        
        # --- 2. The "Premium" AI Analysis Section ---
        if st.button("Run AI Strategic Analysis", type="primary"):
            with st.spinner("Connecting to Gemini AI for deep analysis... This may take a moment."):
                try:
                    analysis_url = f"{API_URL}/ai-strategic-analysis?company_id={company_id}"
                    response = requests.get(analysis_url)
                    response.raise_for_status()
                    analysis_data = response.json()
                    
                    st.subheader("🤖 AI Strategic Report")
                    # The 'analysis' text from the AI is already formatted with titles, so we can just display it.
                    st.markdown(analysis_data['analysis']) 
                    st.caption(f"This report was generated from {analysis_data['feedback_count']} feedback entries.")

                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to generate analysis: {e.response.json()['detail']}")
        
        st.divider()
        
        # --- 3. Other Potential Premium Features (Future Ideas) ---
        st.subheader("Future Premium Features")
        st.info(" A premium tier with features like sentiment analysis, urgency detection, and competitor tracking.")
