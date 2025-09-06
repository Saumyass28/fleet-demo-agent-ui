import streamlit as st
import pandas as pd
import sqlite3

DB_PATH = "fleet_demo.db"

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


# ---------------- UI ----------------
st.set_page_config(page_title="Fleet Agent Demo", layout="wide")
st.title("🚛 Commercial Fleet Agent Demo")
st.write("Explore OEMs, dealers, reviews, and vehicle comparisons using live data from SQLite.")

# Section 1: OEM Search
st.header("1️⃣ Find OEMs in Your Area")
city = st.selectbox("Select City", get_cities())
oem_df = get_oems(city)

st.subheader(f"Available OEMs in {city}")
if not oem_df.empty:
    # dynamically show only the columns that exist
    st.dataframe(oem_df)
else:
    st.info("No OEMs found for this city.")

# Section 2: Dealer Shortlisting
st.header("2️⃣ Shortlist Dealers by Vehicle Type")
vehicle_type = st.selectbox("Choose Vehicle Type", get_vehicle_types())
budget = st.slider("Select Budget (in Lakhs)", 10, 50, 25)

dealer_df = get_vehicles(vehicle_type, budget)
if not dealer_df.empty:
    st.subheader("Matching Dealers and Vehicles")
    st.dataframe(dealer_df)
else:
    st.info("No dealers found matching your filters.")

# Section 3: Vehicle Reviews
st.header("3️⃣ Read Vehicle Reviews")
model_choice = st.selectbox("Select Model", get_models())
reviews = get_reviews(model_choice)

if reviews:
    for r in reviews:
        st.write(f"⭐ {r['rating']} - {r['comment']}")
else:
    st.info("No reviews found for this model.")

# Section 4: Compare Models
st.header("4️⃣ Compare Models")
models_to_compare = st.multiselect("Select Models to Compare", get_models())

if len(models_to_compare) >= 2:
    compare_df = compare_models(models_to_compare)
    st.dataframe(compare_df.set_index("model"))
else:
    st.info("Please select at least 2 models to compare.")
