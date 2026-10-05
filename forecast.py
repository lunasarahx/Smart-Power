import pandas as pd
import joblib
from datetime import date, timedelta

# Load model
model = joblib.load("models/demand_model.pkl")

# Fuel codes
fuel_codes = {
    "Petrol": 0,
    "Diesel": 1,
    "CNG": 2
}

# Starting values
prices = {
    "Petrol": 104.50,
    "Diesel": 92.50,
    "CNG": 85.00
}

temperatures = {
    "Petrol": 28,
    "Diesel": 28,
    "CNG": 28
}

stocks = {
    "Petrol": 7000,
    "Diesel": 6000,
    "CNG": 4000
}

# Start from tomorrow
start_date = date.today() + timedelta(days=1)

forecast = []

for i in range(7):

    prediction_date = start_date + timedelta(days=i)

    for fuel in ["Petrol", "Diesel", "CNG"]:

        input_data = pd.DataFrame([{
            "fuel_code": fuel_codes[fuel],
            "price": prices[fuel],
            "holiday": 0,
            "temperature": temperatures[fuel],
            "stock": stocks[fuel],
            "day": prediction_date.day,
            "month": prediction_date.month,
            "day_of_week": prediction_date.weekday()
        }])

        prediction = model.predict(input_data)[0]

        forecast.append({
            "Date": prediction_date,
            "Fuel": fuel,
            "Predicted Demand (L)": round(prediction)
        })

forecast_df = pd.DataFrame(forecast)

print("\n7-DAY FUEL DEMAND FORECAST")
print("--------------------------------")

print(forecast_df.to_string(index=False))