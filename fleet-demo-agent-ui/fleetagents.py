import streamlit as st
import pandas as pd
import sqlite3

DB_FILE = "fleet_demo.db"

# ---------- Query Helpers ----------
def get_cities():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT DISTINCT city FROM oems", conn)
    conn.close()
    return df["city"].tolist()

def get_vehicle_types():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT DISTINCT type FROM vehicles", conn)
    conn.close()
    return df["type"].tolist()

def get_models():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT DISTINCT model FROM vehicles", conn)
    conn.close()
    return df["model"].tolist()

def get_oems(city):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(f"SELECT * FROM oems WHERE city='{city}'", conn)
    conn.close()
    return df

def get_vehicles(vehicle_type, budget):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(f"""
        SELECT * FROM vehicles 
        WHERE type='{vehicle_type}' AND price_lakhs <= {budget}
    """, conn)
    conn.close()
    return df

def get_reviews(model):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql(f"SELECT rating, comment FROM reviews WHERE model='{model}'", conn)
    conn.close()
    return df.to_dict(orient="records")

def compare_models(models):
    if not models:
        return pd.DataFrame()
    conn = sqlite3.connect(DB_FILE)
    placeholder = ",".join([f"'{m}'" for m in models])
    df = pd.read_sql(f"SELECT * FROM vehicles WHERE model IN ({placeholder})", conn)
    conn.close()
    return df

# ---------- Streamlit App ----------
st.set_page_config(page_title="Fleet Agent Demo", layout="wide")

# App title
st.title("🚛 Commercial Fleet Agent Demo")
st.write("Demo connected to SQLite DB instead of JSON.")

# Sidebar for all inputs (UI same as JSON version)
with st.sidebar:
    st.header("⚙️ Filters & Options")

    city = st.selectbox("Select City", get_cities())
    vehicle_type = st.selectbox("Choose Vehicle Type", get_vehicle_types())
    budget = st.slider("Select Budget (in Lakhs)", 10, 60, 25)
    model_choice = st.selectbox("Select Model for Reviews", get_models())
    models_to_compare = st.multiselect("Select Models to Compare", get_models())

# Main content (UI same as JSON version)
# Section 1: OEMs
st.header("1️⃣ OEMs in Your Area")
oem_df = get_oems(city)
st.dataframe(oem_df[["name", "contact", "city"]])

# Section 2: Dealer Shortlisting
st.header("2️⃣ Matching Dealers and Vehicles")
vehicles = get_vehicles(vehicle_type, budget)
if not vehicles.empty:
    st.table(vehicles[["model", "dealer", "price_lakhs"]])
else:
    st.info("No dealers found matching your filters.")

# Section 3: Vehicle Reviews
st.header(f"3️⃣ Reviews for {model_choice}")
reviews = get_reviews(model_choice)
if reviews:
    for r in reviews:
        st.write(f"⭐ {r['rating']} - {r['comment']}")
else:
    st.info("No reviews found for this model.")

# Section 4: Compare Models
st.header("4️⃣ Compare Selected Models")
if len(models_to_compare) >= 2:
    compare_df = compare_models(models_to_compare)
    st.dataframe(compare_df.set_index("model"))
else:
    st.info("Please select at least 2 models to compare.")
