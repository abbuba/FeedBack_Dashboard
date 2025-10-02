import streamlit as st
import requests
import pandas as pd

# Page Config
st.set_page_config(page_title="Leadership Feedback Dashboard", layout="wide", page_icon="📈")
st.title("📈 AI-Powered Field Agent Dashboard")

# API URL
API_URL = "https://ai-feedback-pj5y.onrender.com"

# Helper function to fetch data from API
@st.cache_data(ttl=300)
def get_data(endpoint):
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

# --- Load All Initial Data ---
feedback_with_topics = get_data("feedback-with-topics")
all_topics_defs = get_data("topics")
all_companies = get_data("companies")
all_regions = get_data("regions")

if not feedback_with_topics:
    st.warning("Not enough feedback data has been submitted yet to generate insights. Please use the app to submit at least 5 feedback entries.")
else:
    df = pd.DataFrame(feedback_with_topics)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filters")

    # Company Filter (for summarizer)
    company_map = {comp['name']: comp['id'] for comp in all_companies}
    selected_company_name = st.sidebar.selectbox("Company", options=company_map.keys())

    # Product Filter (dynamic based on company)
    selected_product_name = None
    if selected_company_name:
        company_id = company_map[selected_company_name]
        products = get_data(f"companies/{company_id}/products")
        if products:
            product_map = {prod['name']: prod['id'] for prod in products}
            selected_product_name = st.sidebar.selectbox("Product", options=product_map.keys())

    # Region Filter
    selected_region = st.sidebar.selectbox("Region", options=["All"] + all_regions)
    
    # Topic Filter
    topic_map = {f"Topic {t['topic_id']}: {', '.join(t['top_words'])}": t['topic_id'] for t in all_topics_defs.get('topics', [])}
    selected_topic_key = st.sidebar.selectbox("AI-Discovered Topic", options=["All"] + list(topic_map.keys()))

    # --- Filtering Logic ---
    filtered_df = df.copy()
    if selected_region != "All":
        filtered_df = filtered_df[filtered_df['agent_region'] == selected_region]
    if selected_topic_key != "All":
        topic_id = topic_map[selected_topic_key]
        filtered_df = filtered_df[filtered_df['predicted_topic'] == topic_id]

    # --- Main Dashboard Display ---
    st.header("Filtered Feedback Entries")
    st.dataframe(filtered_df[['timestamp', 'agent_region', 'product_name', 'feedback_text']])
    
    st.divider()

    # --- AI Summarization Section ---
    st.header("🤖 Google Gemini AI Summarizer")
    if st.sidebar.button("Generate Summary", type="primary"):
        if selected_product_name and selected_region != "All":
            product_id = product_map[selected_product_name]
            with st.spinner(f"Asking Gemini for a summary of '{selected_product_name}' in '{selected_region}'..."):
                try:
                    summary_url = f"{API_URL}/summarize?product_id={product_id}&region={selected_region}"
                    response = requests.get(summary_url)
                    response.raise_for_status()
                    summary_data = response.json()
                    
                    st.subheader("AI-Generated Summary")
                    st.success(f"**Key Takeaways:** {summary_data['summary']}")
                    st.caption(f"This summary is based on {summary_data['feedback_count']} feedback entries.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to generate summary: {e.response.json()['detail']}")
        else:
            st.sidebar.warning("Please select a Product and a specific Region to generate a summary.")
