import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

DB_PATH = "fleet_demo.db"

# Custom CSS for professional corporate styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .main-header p {
        color: #e8f4fd;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        text-align: center;
    }
    
    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #2a5298;
    }
    
    .section-header {
        color: #1e3c72;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 6px;
        text-align: center;
        border: 1px solid #dee2e6;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3c72;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    .review-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #28a745;
    }
    
    .rating {
        color: #ffc107;
        font-size: 1.2rem;
    }
    
    .stSelectbox > div > div {
        background-color: white;
        border: 2px solid #e9ecef;
        border-radius: 6px;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
    }
    
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

def get_oems(city: str):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM oems WHERE city = ?"
    df = pd.read_sql_query(query, conn, params=(city,))
    conn.close()
    return df

def get_cities():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT DISTINCT city FROM oems"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return sorted(df["city"].tolist())

def get_vehicle_types():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT DISTINCT type FROM vehicles"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return sorted(df["type"].tolist())

def get_vehicles(vehicle_type, budget):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM vehicles WHERE type = ? AND price_lakhs <= ?"
    df = pd.read_sql_query(query, conn, params=(vehicle_type, budget))
    conn.close()
    return df

def get_models():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT DISTINCT model FROM vehicles"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df["model"].tolist()

def get_reviews(model):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT rating, comment FROM reviews WHERE model = ?"
    df = pd.read_sql_query(query, conn, params=(model,))
    conn.close()
    return df.to_dict("records")

def compare_models(models):
    conn = sqlite3.connect(DB_PATH)
    placeholders = ",".join("?" * len(models))
    query = f"SELECT * FROM vehicles WHERE model IN ({placeholders})"
    df = pd.read_sql_query(query, conn, params=models)
    conn.close()
    return df

def get_fleet_analytics():
    conn = sqlite3.connect(DB_PATH)
    
    # Get vehicle count by type
    vehicle_types = pd.read_sql("SELECT type, COUNT(*) as count FROM vehicles GROUP BY type", conn)
    
    # Get average price by type
    avg_prices = pd.read_sql("SELECT type, AVG(price_lakhs) as avg_price FROM vehicles GROUP BY type", conn)
    
    # Get city distribution
    city_dist = pd.read_sql("SELECT city, COUNT(*) as oem_count FROM oems GROUP BY city", conn)
    
    conn.close()
    return vehicle_types, avg_prices, city_dist

# ---------------- UI ----------------
st.set_page_config(
    page_title="Fleet Management System", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚛"
)

# Main Header
st.markdown("""
<div class="main-header">
    <h1>Fleet Management System</h1>
    <p>Professional Fleet Analytics & Vehicle Management Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for filters
with st.sidebar:
    st.markdown("### **Fleet Analytics Dashboard**")
    st.markdown("---")
    
    st.markdown("#### **Search Filters**")
    city = st.selectbox("Select City", get_cities(), key="city_filter")
    vehicle_type = st.selectbox("Choose Vehicle Type", get_vehicle_types(), key="vehicle_filter")
    budget = st.slider("Budget Range (Lakhs)", 10, 50, 25, key="budget_filter")
    
    st.markdown("---")
    st.markdown("#### **Review & Comparison**")
    model_choice = st.selectbox("Select Model for Reviews", get_models(), key="review_model")
    models_to_compare = st.multiselect("Select Models to Compare", get_models(), key="compare_models")
    
    st.markdown("---")
    st.markdown("#### **Quick Stats**")
    
    # Get analytics data
    vehicle_types, avg_prices, city_dist = get_fleet_analytics()
    
    total_vehicles = vehicle_types['count'].sum()
    total_oems = city_dist['oem_count'].sum()
    
    st.metric("Total Vehicles", total_vehicles)
    st.metric("Total OEMs", total_oems)
    st.metric("Cities Covered", len(city_dist))

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    # Section 1: OEM Search
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🏢 OEM Directory</div>', unsafe_allow_html=True)
    
    oem_df = get_oems(city)
    
    if not oem_df.empty:
        st.markdown(f"**Available OEMs in {city}**")
        
        # Display OEMs in a more professional format
        for _, oem in oem_df.iterrows():
            with st.expander(f"**{oem.get('name', 'N/A')}** - {oem.get('contact', 'N/A')}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**City:** {oem.get('city', 'N/A')}")
                    st.write(f"**Contact:** {oem.get('contact', 'N/A')}")
                with col_b:
                    st.write(f"**Address:** {oem.get('address', 'N/A')}")
                    st.write(f"**Phone:** {oem.get('phone', 'N/A')}")
    else:
        st.info("No OEMs found for this city.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Quick Analytics
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Quick Analytics</div>', unsafe_allow_html=True)
    
    # Vehicle type distribution
    if not vehicle_types.empty:
        fig = px.pie(vehicle_types, values='count', names='type', 
                    title="Vehicle Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Section 2: Dealer Shortlisting
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">🚗 Vehicle Search & Filtering</div>', unsafe_allow_html=True)

dealer_df = get_vehicles(vehicle_type, budget)

if not dealer_df.empty:
    st.markdown(f"**Matching Vehicles: {len(dealer_df)} found**")
    
    # Display vehicles in a more professional table format
    display_df = dealer_df[['model', 'dealer', 'price_lakhs', 'type']].copy()
    display_df.columns = ['Model', 'Dealer', 'Price (Lakhs)', 'Type']
    display_df['Price (Lakhs)'] = display_df['Price (Lakhs)'].round(2)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Price analysis
    if len(dealer_df) > 1:
        avg_price = dealer_df['price_lakhs'].mean()
        min_price = dealer_df['price_lakhs'].min()
        max_price = dealer_df['price_lakhs'].max()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price", f"₹{avg_price:.1f}L")
        with col2:
            st.metric("Lowest Price", f"₹{min_price:.1f}L")
        with col3:
            st.metric("Highest Price", f"₹{max_price:.1f}L")
else:
    st.info("No vehicles found matching your criteria. Try adjusting your filters.")
    
st.markdown('</div>', unsafe_allow_html=True)

# Section 3: Vehicle Reviews
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">⭐ Customer Reviews & Ratings</div>', unsafe_allow_html=True)

reviews = get_reviews(model_choice)

if reviews:
    st.markdown(f"**Customer Reviews for {model_choice}**")
    
    # Calculate average rating
    avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_rating:.1f}/5</div>
            <div class="metric-label">Average Rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**Based on {len(reviews)} customer reviews**")
    
    # Display individual reviews
    for i, r in enumerate(reviews):
        stars = "★" * int(r['rating']) + "☆" * (5 - int(r['rating']))
        st.markdown(f"""
        <div class="review-card">
            <div class="rating">{stars}</div>
            <div style="margin-top: 0.5rem;">{r['comment']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No reviews available for this model.")
    
st.markdown('</div>', unsafe_allow_html=True)

# Section 4: Model Comparison
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">⚖️ Vehicle Comparison Tool</div>', unsafe_allow_html=True)

if len(models_to_compare) >= 2:
    compare_df = compare_models(models_to_compare)
    
    if not compare_df.empty:
        st.markdown(f"**Comparing {len(models_to_compare)} models**")
        
        # Create comparison table
        comparison_data = compare_df.set_index("model")
        display_cols = ['dealer', 'price_lakhs', 'type']
        comparison_display = comparison_data[display_cols].copy()
        comparison_display.columns = ['Dealer', 'Price (Lakhs)', 'Type']
        comparison_display['Price (Lakhs)'] = comparison_display['Price (Lakhs)'].round(2)
        
        st.dataframe(
            comparison_display,
            use_container_width=True
        )
        
        # Price comparison chart
        if len(compare_df) > 1:
            fig = px.bar(
                compare_df, 
                x='model', 
                y='price_lakhs',
                title="Price Comparison",
                color='price_lakhs',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                xaxis_title="Model",
                yaxis_title="Price (Lakhs)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected models.")
else:
    st.info("Please select at least 2 models to compare.")
    
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6c757d; padding: 1rem;">
    <p>Fleet Management System | Professional Fleet Analytics Platform</p>
    <p>Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%B %d, %Y at %I:%M %p")), unsafe_allow_html=True)
