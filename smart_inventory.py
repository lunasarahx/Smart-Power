import pandas as pd
import joblib
from datetime import date, timedelta

# Load AI model
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

# Current inventory
inventory = {
    "Petrol": 7000,
    "Diesel": 6000,
    "CNG": 4000
}

temperature = 28

# Safety stock = extra fuel kept as a buffer
safety_days = 2

results = []

for fuel in ["Petrol", "Diesel", "CNG"]:

    total_demand = 0

    # Predict next 7 days
    for i in range(7):

        prediction_date = (
            date.today() + timedelta(days=i + 1)
        )

        input_data = pd.DataFrame([{
            "fuel_code": fuel_codes[fuel],
            "price": prices[fuel],
            "holiday": 0,
            "temperature": temperature,
            "stock": inventory[fuel],
            "day": prediction_date.day,
            "month": prediction_date.month,
            "day_of_week": prediction_date.weekday()
        }])

        prediction = model.predict(input_data)[0]

        total_demand += prediction

    # Average daily demand
    average_demand = total_demand / 7

    # Safety stock
    safety_stock = average_demand * safety_days

    # Required stock
    required_stock = total_demand + safety_stock

    # Current inventory
    current_stock = inventory[fuel]

    # Recommended order
    recommended_order = max(
        0,
        required_stock - current_stock
    )

    # Inventory status
    if current_stock < average_demand:
        status = "CRITICAL"

    elif current_stock < required_stock:
        status = "REORDER"

    else:
        status = "NORMAL"

    results.append({
        "Fuel": fuel,
        "Current Stock (L)": round(current_stock),
        "7-Day Demand (L)": round(total_demand),
        "Safety Stock (L)": round(safety_stock),
        "Recommended Order (L)": round(recommended_order),
        "Status": status
    })


# Create table
result_df = pd.DataFrame(results)

print("\nSMARTPOWER INVENTORY RECOMMENDATION")
print("====================================")

print(result_df.to_string(index=False))