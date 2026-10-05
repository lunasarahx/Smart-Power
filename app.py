import streamlit as st
import pandas as pd
import joblib
from datetime import date, timedelta

# =========================================================
# LOAD DATA + AI MODEL
# =========================================================

df = pd.read_csv("data/fuel_data.csv")
df["date"] = pd.to_datetime(df["date"])

model = joblib.load("models/demand_model.pkl")

fuel_codes = {
    "Petrol": 0,
    "Diesel": 1,
    "CNG": 2
}

prices = {
    "Petrol": 104.50,
    "Diesel": 92.50,
    "CNG": 85.00
}


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="SmartPower",
    page_icon="⛽",
    layout="wide"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⛽ SmartPower")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🔮 Demand Prediction",
        "📈 7-Day Forecast",
        "📦 Inventory Management"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "🏠 Dashboard":

    st.title("⛽ SmartPower")

    st.subheader(
        "AI-Based Fuel Demand Prediction & Inventory Management"
    )

    st.divider()

    # KPIs
    total_sales = df["sales_litres"].sum()

    average_demand = df["sales_litres"].mean()

    total_stock = df["stock"].sum()

    low_stock = (
        df["stock"] < df["sales_litres"]
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "⛽ Total Fuel Sold",
        f"{total_sales:,.0f} L"
    )

    col2.metric(
        "📊 Average Daily Demand",
        f"{average_demand:,.0f} L"
    )

    col3.metric(
        "📦 Total Inventory",
        f"{total_stock:,.0f} L"
    )

    col4.metric(
        "🚨 Low Stock Records",
        low_stock
    )

    st.divider()

    # Demand graph
    st.subheader("📈 Historical Fuel Demand")

    daily_demand = (
        df.groupby("date")["sales_litres"]
        .sum()
    )

    st.line_chart(daily_demand)

    st.divider()

    # Fuel comparison
    st.subheader("⛽ Fuel Demand Comparison")

    fuel_demand = (
        df.groupby("fuel_type")["sales_litres"]
        .sum()
    )

    st.bar_chart(fuel_demand)


# =========================================================
# DEMAND PREDICTION
# =========================================================

elif page == "🔮 Demand Prediction":

    st.title("🔮 AI Fuel Demand Prediction")

    st.write(
        "Enter the expected conditions and let the AI predict demand."
    )

    col1, col2 = st.columns(2)

    with col1:

        fuel = st.selectbox(
            "Fuel Type",
            ["Petrol", "Diesel", "CNG"]
        )

        price = st.number_input(
            "Fuel Price (₹)",
            min_value=1.0,
            value=prices[fuel]
        )

        holiday = st.selectbox(
            "Holiday?",
            ["No", "Yes"]
        )

    with col2:

        temperature = st.number_input(
            "Temperature (°C)",
            min_value=0.0,
            max_value=50.0,
            value=28.0
        )

        stock = st.number_input(
            "Current Stock (L)",
            min_value=0.0,
            value=5000.0
        )

        prediction_date = st.date_input(
            "Prediction Date",
            value=date.today()
        )

    st.divider()

    if st.button(
        "🔮 Predict Demand",
        use_container_width=True
    ):

        fuel_code = fuel_codes[fuel]

        holiday_value = (
            1 if holiday == "Yes" else 0
        )

        input_data = pd.DataFrame([{

            "fuel_code": fuel_code,

            "price": price,

            "holiday": holiday_value,

            "temperature": temperature,

            "stock": stock,

            "day": prediction_date.day,

            "month": prediction_date.month,

            "day_of_week": prediction_date.weekday()

        }])

        prediction = model.predict(input_data)[0]

        st.success(
            f"### Predicted {fuel} Demand: "
            f"{prediction:,.0f} L"
        )

        if stock < prediction:

            shortage = prediction - stock

            st.error(
                f"🚨 Inventory Warning\n\n"
                f"You may need approximately "
                f"{shortage:,.0f} L more."
            )

        else:

            remaining = stock - prediction

            st.info(
                f"✅ Inventory sufficient\n\n"
                f"Expected remaining stock: "
                f"{remaining:,.0f} L"
            )


# =========================================================
# 7-DAY FORECAST
# =========================================================

elif page == "📈 7-Day Forecast":

    st.title("📈 AI 7-Day Fuel Demand Forecast")

    st.write(
        "SmartPower predicts the expected fuel demand "
        "for the next 7 days."
    )

    forecast = []

    for i in range(7):

        prediction_date = (
            date.today()
            + timedelta(days=i + 1)
        )

        for fuel in [
            "Petrol",
            "Diesel",
            "CNG"
        ]:

            # Find latest stock for this fuel
            fuel_rows = df[
                df["fuel_type"] == fuel
            ]

            current_stock = fuel_rows.iloc[-1]["stock"]

            input_data = pd.DataFrame([{

                "fuel_code": fuel_codes[fuel],

                "price": prices[fuel],

                "holiday": 0,

                "temperature": 28,

                "stock": current_stock,

                "day": prediction_date.day,

                "month": prediction_date.month,

                "day_of_week":
                    prediction_date.weekday()

            }])

            prediction = model.predict(
                input_data
            )[0]

            forecast.append({

                "Date": prediction_date,

                "Fuel": fuel,

                "Predicted Demand (L)":
                    round(prediction)

            })

    forecast_df = pd.DataFrame(forecast)

    # Display table
    st.subheader("🔮 Forecast Table")

    pivot = forecast_df.pivot(
        index="Date",
        columns="Fuel",
        values="Predicted Demand (L)"
    )

    st.dataframe(
        pivot,
        use_container_width=True
    )

    st.divider()

    # Graph
    st.subheader("📊 Forecast Trend")

    st.line_chart(
        pivot
    )


# =========================================================
# INVENTORY MANAGEMENT
# =========================================================

elif page == "📦 Inventory Management":

    st.title("📦 Smart Inventory Management")

    fuel = st.selectbox(
        "Select Fuel",
        ["Petrol", "Diesel", "CNG"]
    )

    fuel_data = df[
        df["fuel_type"] == fuel
    ]

    current_stock = fuel_data.iloc[-1]["stock"]

    # Predict next 7 days
    total_demand = 0

    for i in range(7):

        prediction_date = (
            date.today()
            + timedelta(days=i + 1)
        )

        input_data = pd.DataFrame([{

            "fuel_code":
                fuel_codes[fuel],

            "price":
                prices[fuel],

            "holiday":
                0,

            "temperature":
                28,

            "stock":
                current_stock,

            "day":
                prediction_date.day,

            "month":
                prediction_date.month,

            "day_of_week":
                prediction_date.weekday()

        }])

        prediction = model.predict(
            input_data
        )[0]

        total_demand += prediction

    # Average demand
    average_demand = (
        total_demand / 7
    )

    # Safety stock
    safety_stock = (
        average_demand * 2
    )

    # Total required
    required_stock = (
        total_demand
        + safety_stock
    )

    # Recommended order
    recommended_order = max(
        0,
        required_stock - current_stock
    )

    # Days remaining
    if average_demand > 0:

        days_remaining = (
            current_stock
            / average_demand
        )

    else:

        days_remaining = 0

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📦 Current Stock",
        f"{current_stock:,.0f} L"
    )

    col2.metric(
        "📊 7-Day Demand",
        f"{total_demand:,.0f} L"
    )

    col3.metric(
        "⏳ Stock Days",
        f"{days_remaining:.1f}"
    )

    col4.metric(
        "🛒 Recommended Order",
        f"{recommended_order:,.0f} L"
    )

    st.divider()

    # -----------------------------------------------------
    # STATUS
    # -----------------------------------------------------

    if days_remaining < 1:

        st.error(
            "🔴 CRITICAL — Fuel may run out very soon!"
        )

    elif current_stock < required_stock:

        st.warning(
            "🟠 REORDER REQUIRED"
        )

    else:

        st.success(
            "🟢 INVENTORY NORMAL"
        )

    st.divider()

    # -----------------------------------------------------
    # AI RECOMMENDATION
    # -----------------------------------------------------

    st.subheader("🤖 SmartPower Recommendation")

    if recommended_order > 0:

        st.write(
            f"Based on the predicted 7-day demand, "
            f"SmartPower recommends ordering "
            f"**{recommended_order:,.0f} litres of "
            f"{fuel}**."
        )

        st.write(
            f"This recommendation includes "
            f"approximately **{safety_stock:,.0f} L** "
            f"of safety stock."
        )

    else:

        st.write(
            f"Current {fuel} inventory is sufficient "
            f"for the predicted demand."
        )

    st.divider()

    # -----------------------------------------------------
    # INVENTORY HISTORY
    # -----------------------------------------------------

    st.subheader("📦 Inventory History")

    inventory_history = (
        fuel_data
        .groupby("date")["stock"]
        .mean()
    )

    st.line_chart(
        inventory_history
    )