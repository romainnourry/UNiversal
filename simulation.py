import streamlit as st
import pandas as pd
import random

# ---------------------------
# Simulation Function
# ---------------------------
def simulate_universal_economy(num_people, num_businesses, num_landlords, num_steps):
    people = []
    businesses = []
    landlords = []

    for _ in range(num_people):
        income = random.randint(20000, 50000)
        rent = random.randint(800, 2000)
        capital = income * random.uniform(0.0, 0.1)
        target_capital = income * 0.25
        gap = max(0, target_capital - capital)
        universals = gap * 0.5
        spending = income * random.uniform(0.5, 0.85)
        universal_spending = spending * random.uniform(0.4, 0.9) * 0.2
        wealth = capital + universals

        people.append({
            "Income": income,
            "Rent": rent,
            "Capital": capital,
            "Universals": universals,
            "Spending": spending,
            "Universal_Spending": universal_spending,
            "Wealth": wealth
        })

    for _ in range(num_businesses):
        annual_revenue = random.randint(100000, 300000)
        universals_received = random.randint(100, 1000) * num_steps
        businesses.append({
            "Annual_Revenue": annual_revenue,
            "Universals_Received": universals_received
        })

    for _ in range(num_landlords):
        monthly_rent = random.randint(10000, 30000)
        total_rent = monthly_rent * num_steps
        landlords.append({
            "Total_Rent": total_rent
        })

    return pd.DataFrame(people), pd.DataFrame(businesses), pd.DataFrame(landlords)

# ---------------------------
# Streamlit Interface
# ---------------------------
st.set_page_config(page_title="Simple Universal Economy Simulation", layout="wide")
st.title("Universal Capital Redistribution – Minimal Simulation")

num_people = st.sidebar.slider("Number of residents", 100, 1000, 500)
num_businesses = st.sidebar.slider("Number of businesses", 10, 200, 100)
num_landlords = st.sidebar.slider("Number of landlords", 1, 20, 10)
num_steps = st.sidebar.slider("Simulation steps (e.g., months)", 1, 50, 12)

people_df, business_df, landlord_df = simulate_universal_economy(
    num_people, num_businesses, num_landlords, num_steps
)

st.subheader("Resident Summary")
st.dataframe(people_df.sort_values("Universals", ascending=False))

st.subheader("Business Summary")
st.dataframe(business_df)

st.subheader("Landlord Summary")
st.dataframe(landlord_df)

st.subheader("Universal Spending Distribution")
st.bar_chart(people_df["Universal_Spending"])
