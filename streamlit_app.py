
import streamlit as st
import pandas as pd
import os
import uuid
import time
from typing import Optional, Any
from dotenv import load_dotenv

# Import our project logic
from phase2.services.database_service import DatabaseService
from phase2.services.recommendation_service import RecommendationService
from phase4.query_parser import parse_natural_language_query

# Load environment variables
load_dotenv()

# Zomato-brand aesthetic
st.set_page_config(
    page_title="Zomato AI Restaurant Recommender",
    page_icon="🍴",
    layout="wide",
)

# Custom CSS for Zomato branding
st.markdown("""
<style>
    :root {
        --accent: #e23744;
    }
    .main {
        background-color: #f7f7f7;
    }
    .stButton>button {
        background-color: #e23744;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        width: 100%;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #cb202d;
        color: white;
    }
    h1, h2, h3 {
        color: #1c1c1c;
    }
    .restaurant-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .rating-badge {
        background-color: #f5f5f5;
        color: #e23744;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.85rem;
    }
    .summary-box {
        background-color: #ffffff;
        border-left: 5px solid #e23744;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .meta-text {
        font-size: 0.85rem;
        color: #6b7280;
    }
    .price-text {
        font-weight: 600;
        color: #1c1c1c;
    }
</style>
""", unsafe_allow_html=True)

# Cuisine Image Map
IMAGE_BY_CUISINE = {
    'default': 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&q=80',
    'north indian': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80',
    'chinese': 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=400&q=80',
    'italian': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80',
    'cafe': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80',
    'south indian': 'https://images.unsplash.com/photo-1631452180519-c014fe442f9a?w=400&q=80',
    'mexican': 'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&q=80',
    'continental': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&q=80',
    'biryani': 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80',
    'american': 'https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&q=80',
    'burger': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80',
    'healthy': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&q=80',
    'salad': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80',
}

def get_image_for_cuisine(cuisine: str) -> str:
    if not cuisine: return IMAGE_BY_CUISINE['default']
    parts = cuisine.lower().replace(",", " ").split()
    for part in parts:
        if part in IMAGE_BY_CUISINE: return IMAGE_BY_CUISINE[part]
        if 'indian' in part: return IMAGE_BY_CUISINE['north indian']
        if 'healthy' in part: return IMAGE_BY_CUISINE['healthy']
    return IMAGE_BY_CUISINE['default']

# Title Section
st.markdown("<h1 style='text-align: center; color: #e23744;'>Zomato AI Restaurant Recommender</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 2rem;'>Helping you find the best places to eat in <span style='color:#e23744; font-weight:600;'>Bangalore</span> city</p>", unsafe_allow_html=True)

# Data Fetching for Options
@st.cache_data
def load_options():
    try:
        db = DatabaseService()
        df = db.get_all_restaurants()
        if len(df) == 0:
            return [], []
        
        locations = sorted(df["location"].dropna().astype(str).str.strip().unique().tolist())
        locations = [x for x in locations if x]
        
        cuisines_set = set()
        for col in ["cuisine_list", "cuisine"]:
            if col in df.columns:
                for v in df[col].dropna():
                    for part in str(v).replace("|", ",").split(","):
                        p = part.strip().title()
                        if p: cuisines_set.add(p)
        cuisines = sorted(list(cuisines_set))
        
        return locations, cuisines
    except Exception:
        return [], []

locations, cuisines = load_options()

# Sidebar / Filters
st.sidebar.title("Search Filters")
with st.sidebar:
    selected_location = st.selectbox("Location", ["Any"] + locations)
    selected_cuisine = st.selectbox("Cuisine", ["Any"] + cuisines)
    
    price_tier = st.selectbox("Price Range", [
        "Any",
        "Budget friendly (≤ ₹500)",
        "Mid-range (₹500–₹1500)",
        "Premium (> ₹1500)"
    ])
    
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)
    limit = st.number_input("Result Limit", 1, 20, 5)

# Main UI
nl_query = st.text_input("Or just describe what you want", placeholder="e.g. Romantic place for dinner under ₹1500", help="AI will extract location, cuisine, and price from your text.")

if st.button("Find Restaurants"):
    with st.spinner("Finding the best matches for you..."):
        # Process Search
        location = selected_location if selected_location != "Any" else ""
        cuisine = selected_cuisine if selected_cuisine != "Any" else None
        m_rating = min_rating if min_rating > 0 else None
        
        cost_min, cost_max = None, None
        if price_tier == "Budget friendly (≤ ₹500)": cost_max = 500.0
        elif price_tier == "Mid-range (₹500–₹1500)": cost_min, cost_max = 501.0, 1500.0
        elif price_tier == "Premium (> ₹1500)": cost_min = 1501.0
        
        # Merge with Natural Language
        if nl_query.strip():
            extracted = parse_natural_language_query(nl_query.strip())
            if extracted.get("location") and not location: location = extracted["location"]
            if extracted.get("cuisine") and not cuisine: cuisine = extracted["cuisine"]
            if extracted.get("min_rating") is not None and m_rating is None: m_rating = extracted["min_rating"]
            if extracted.get("cost_min") is not None and cost_min is None: cost_min = extracted["cost_min"]
            if extracted.get("cost_max") is not None and cost_max is None: cost_max = extracted["cost_max"]
        
        if not location:
            location = "Bangalore"
        
        # Instantiate services
        service = RecommendationService()
        
        recommendations_df, total_found, llm_result = service.get_recommendations(
            location=location,
            cuisine=cuisine,
            min_rating=m_rating,
            cost_min=cost_min,
            cost_max=cost_max,
            limit=limit,
            include_explanations=True
        )
        
        # Display Results
        if total_found > 0:
            st.success(f"Found {total_found} matches. Showing the best {len(recommendations_df)} results.")
            
            # AI Summary
            if llm_result and llm_result.get("summary"):
                st.markdown(f"""
                <div class="summary-box">
                    <p style='color:#e23744; font-weight:600; margin-bottom:0.5rem;'>✨ AI Summary</p>
                    <p class="summaryBoxText">{llm_result['summary']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Restaurant Cards
            for _, rec in recommendations_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 2.5])
                    with col1:
                        st.image(get_image_for_cuisine(rec['cuisine']), use_column_width=True)
                    with col2:
                        st.markdown(f"### {rec['name']}")
                        st.markdown(f"<span class='rating-badge'>★ {rec['rating']}</span>", unsafe_allow_html=True)
                        
                        meta_html = f"""
                        <div style='margin-top:0.5rem; display:flex; flex-wrap:wrap; gap:1rem;'>
                            <span class='meta-text'>📍 {rec['location']}</span>
                            <span class='meta-text'>🍲 {rec['cuisine']}</span>
                            <span class='meta-text'>💰 <span class='price-text'>₹{int(rec['cost'])}</span> for two</span>
                        </div>
                        """
                        st.markdown(meta_html, unsafe_allow_html=True)
                        
                        if rec.get('explanation'):
                            st.markdown("---")
                            st.markdown(f"<p class='summaryBoxText' style='font-style:italic;'>{rec['explanation']}</p>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("No restaurants found matching your criteria. Try loosening your filters!")
            if llm_result and llm_result.get("summary"):
                st.info(llm_result['summary'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #6b7280; font-size: 0.8rem;'>Powered by Groq LLM & Data Ingestion Pipeline</p>", unsafe_allow_html=True)
