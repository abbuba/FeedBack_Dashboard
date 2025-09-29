import streamlit as st
import requests
import pandas as pd

# Page Config
st.set_page_config(page_title="Leadership Feedback Dashboard", layout="wide")
st.title("📊 AI-Powered Field Agent Feedback Dashboard")

# API URL
API_URL = "https://ai-feedback-pj5y.onrender.com"

# Helper function to fetch data from API
@st.cache_data(ttl=300) # Cache data for 5 minutes
def get_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None # Return None on error

# --- Main App ---
companies = get_data("companies")
regions = get_data("regions")

if not companies:
    st.error("Could not connect to the backend API. Please ensure the server is running.")
else:
    # --- NEW: AI Summarization with Multi-level Filters ---
    st.header("🧠 AI Feedback Summarizer")
    st.write("Select a company, product, and region to generate a summary.")

    # Create dictionaries for easy lookup
    company_names = {comp['name']: comp['id'] for comp in companies}

    # --- Filter Columns ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_company_name = st.selectbox("1. Select a Company", options=company_names.keys())
    
    # --- Dynamic Product Filter ---
    selected_product_name = None
    if selected_company_name:
        company_id = company_names[selected_company_name]
        products = get_data(f"companies/{company_id}/products")
        with col2:
            if products:
                product_names = {prod['name']: prod['id'] for prod in products}
                selected_product_name = st.selectbox("2. Select a Product", options=product_names.keys())
            else:
                st.warning("No products found for this company.")

    # --- Region Filter ---
    with col3:
        selected_region = st.selectbox("3. Select a Region", options=regions or [])

    # --- Generate Summary Button ---
    if st.button("Generate Summary", type="primary"):
        if selected_product_name and selected_region:
            product_id = product_names[selected_product_name]
            with st.spinner("Generating AI summary..."):
                try:
                    summary_url = f"{API_URL}/summarize?product_id={product_id}&region={selected_region}"
                    response = requests.get(summary_url)
                    response.raise_for_status()
                    summary_data = response.json()
                    
                    st.subheader("AI-Generated Summary")
                    st.success(summary_data['summary'])
                    st.caption(f"Based on {summary_data['feedback_count']} feedback entries.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to generate summary: {e.response.json()['detail']}")
        else:
            st.warning("Please select a company, product, and region.")
            
    st.divider()

    # --- Topic Analysis Section ---
    st.header("📊 Overall Topic Analysis")
    if st.button("Analyze All Feedback Topics"):
        with st.spinner("Analyzing topics..."):
            topics_data = get_data("topics")
            if topics_data:
                st.success("Analysis complete! Top themes from all feedback:")
                for topic in topics_data.get("topics", []):
                    st.subheader(f"Theme #{topic['topic_id'] + 1}")
                    st.write(f"**Key Words:** {', '.join(topic['top_words'])}")
