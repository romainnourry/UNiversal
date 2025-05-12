import streamlit as st
import pandas as pd
import random

# ---------------------------
# Simulation Function
# ---------------------------
def simulate_dual_currency_economy(num_people, num_businesses, num_landlords, num_steps):
    people = []
    businesses = []
    landlords = []
    universal_total = 0
    dollar_total = 0

    for _ in range(num_people):
        income = random.randint(20000, 50000)
        rent = random.randint(800, 2000)
        capital = income * random.uniform(0.0, 0.1)
        target_capital = income * 0.25
        gap = max(0, target_capital - capital)
        universals_issued = gap * 0.5

        # Determine price structure of a typical basket
        basket_price = 1000
        capture_ratio = 0.3  # 30% of basket contributes to capital at vendor side
        captured_value = basket_price * capture_ratio
        real_payment = basket_price - (captured_value * 0.5)
        universal_payment = captured_value * 0.5

        # Create more universals for lowest incomes
        income_boost = max(0, 30000 - income)
        extra_universals = income_boost * 0.05
        universals_issued += extra_universals

        spending = income * random.uniform(0.5, 0.85)
        universal_spending = spending * random.uniform(0.4, 0.9) * 0.2
        dollar_spending = spending - universal_spending

        wealth_before = capital
        wealth_after = capital + universals_issued

        people.append({
            "Income": income,
            "Rent": rent,
            "Capital": capital,
            "Universals": universals_issued,
            "Dollar_Spending": dollar_spending,
            "Universal_Spending": universal_spending,
            "Wealth_Before": wealth_before,
            "Wealth_After": wealth_after,
            "Net_Gain": universals_issued,
            "Real_Payment": real_payment,
            "Universal_Payment": universal_payment
        })

        universal_total += universal_spending
        dollar_total += dollar_spending

    for _ in range(num_businesses):
        annual_revenue = random.randint(100000, 300000)
        universals_received = random.randint(100, 1000) * num_steps
        businesses.append({
            "Annual_Revenue": annual_revenue,
            "Universals_Received": universals_received,
            "Net_Gain": universals_received
        })

    for _ in range(num_landlords):
        monthly_rent = random.randint(10000, 30000)
        total_rent = monthly_rent * num_steps
        reinvestment = total_rent * random.uniform(0.05, 0.3)
        net_gain = total_rent - reinvestment
        landlords.append({
            "Total_Rent": total_rent,
            "Reinvestment": reinvestment,
            "Net_Gain": net_gain
        })

    return pd.DataFrame(people), pd.DataFrame(businesses), pd.DataFrame(landlords), universal_total, dollar_total

# ---------------------------
# Streamlit Interface
# ---------------------------
st.set_page_config(page_title="Dual Currency Simulation", layout="wide")
st.title("Dual Currency Economic Simulation – Universals vs Dollars")

num_people = st.sidebar.slider("Number of residents", 100, 1000, 500)
num_businesses = st.sidebar.slider("Number of businesses", 10, 200, 100)
num_landlords = st.sidebar.slider("Number of landlords", 1, 20, 10)
num_steps = st.sidebar.slider("Simulation steps (e.g., months)", 1, 50, 12)

people_df, business_df, landlord_df, universal_total, dollar_total = simulate_dual_currency_economy(
    num_people, num_businesses, num_landlords, num_steps
)

# ---------------------------
# Tabs for Output
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Residents", "Businesses", "Landlords", "Summary & Indicators"])

with tab1:
    st.subheader("Resident Summary")
    st.dataframe(people_df.sort_values("Universals", ascending=False))
    st.subheader("Universal Spending Distribution")
    st.bar_chart(people_df["Universal_Spending"])
    st.subheader("Dollar Spending Distribution")
    st.bar_chart(people_df["Dollar_Spending"])
    st.subheader("Net Wealth Gain from Universals")
    st.bar_chart(people_df["Net_Gain"])

with tab2:
    st.subheader("Business Summary")
    st.dataframe(business_df)
    st.subheader("Universals Received by Businesses")
    st.bar_chart(business_df["Universals_Received"])

with tab3:
    st.subheader("Landlord Summary")
    st.dataframe(landlord_df)
    st.subheader("Landlord Net Gain (after reinvestment)")
    st.bar_chart(landlord_df["Net_Gain"])

with tab4:
    st.subheader("Macroeconomic Indicators")
    total_universals = people_df["Universals"].sum() + business_df["Universals_Received"].sum()
    total_income = people_df["Income"].sum()
    total_rent = landlord_df["Total_Rent"].sum()
    total_capital_before = people_df["Wealth_Before"].sum()
    total_capital_after = people_df["Wealth_After"].sum()
    total_net_gain = people_df["Net_Gain"].sum() + business_df["Net_Gain"].sum() + landlord_df["Net_Gain"].sum()

    purchasing_power_gain = ((total_capital_after - total_capital_before) / total_capital_before * 100) if total_capital_before > 0 else 0

    st.metric("Total Universals Created", f"€{total_universals:,.0f}")
    st.metric("Total Dollar Spending", f"€{dollar_total:,.0f}")
    st.metric("Total Income (Residents)", f"€{total_income:,.0f}")
    st.metric("Total Rent Extracted (Landlords)", f"€{total_rent:,.0f}")
    st.metric("Wealth Before Universals", f"€{total_capital_before:,.0f}")
    st.metric("Wealth After Universals", f"€{total_capital_after:,.0f}")
    st.metric("Purchasing Power Gain (%)", f"{purchasing_power_gain:.1f}%")
    st.metric("Net Value Gained by All Participants", f"€{total_net_gain:,.0f}")

    st.caption("This dashboard distinguishes real (dollar) value from symbolic capital redistribution (universals), revealing how a dual-currency system transforms economic outcomes.")
