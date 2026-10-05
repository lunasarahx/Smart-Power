import pandas as pd
import numpy as np

np.random.seed(42)

dates = pd.date_range(start="2025-01-01", end="2026-09-30", freq="D")

data = []

for date in dates:

    for fuel in ["Petrol", "Diesel", "CNG"]:

        if fuel == "Petrol":
            base_demand = 4500
            price = 104.50

        elif fuel == "Diesel":
            base_demand = 3500
            price = 92.50

        else:
            base_demand = 2200
            price = 85.00

        # Weekend effect
        weekend = date.weekday() >= 5

        if weekend:
            demand = base_demand * 1.15
        else:
            demand = base_demand

        # Random variation
        demand = demand + np.random.normal(0, 400)

        # Holiday
        holiday = np.random.choice([0, 1], p=[0.93, 0.07])

        if holiday:
            demand *= 1.25

        # Temperature
        temperature = np.random.uniform(20, 38)

        # Current stock
        stock = max(0, demand * np.random.uniform(1.0, 2.0))

        data.append([
            date,
            fuel,
            round(demand),
            price,
            holiday,
            round(temperature, 1),
            round(stock)
        ])


df = pd.DataFrame(
    data,
    columns=[
        "date",
        "fuel_type",
        "sales_litres",
        "price",
        "holiday",
        "temperature",
        "stock"
    ]
)

df.to_csv("data/fuel_data.csv", index=False)

print("Dataset created successfully!")
print("Total records:", len(df))