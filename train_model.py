import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# Load our fuel data
df = pd.read_csv("data/fuel_data.csv")

# Convert date into useful information
df["date"] = pd.to_datetime(df["date"])
df["day"] = df["date"].dt.day
df["month"] = df["date"].dt.month
df["day_of_week"] = df["date"].dt.dayofweek

# Convert fuel type into numbers
df["fuel_code"] = df["fuel_type"].map({
    "Petrol": 0,
    "Diesel": 1,
    "CNG": 2
})

# Features used by the AI
X = df[
    [
        "fuel_code",
        "price",
        "holiday",
        "temperature",
        "stock",
        "day",
        "month",
        "day_of_week"
    ]
]

# What we want the AI to predict
y = df["sales_litres"]

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create the AI model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train the model
model.fit(X_train, y_train)

# Check accuracy
accuracy = model.score(X_test, y_test)

print("Model trained successfully!")
print("Model R² score:", round(accuracy, 2))

# Save the trained model
joblib.dump(model, "models/demand_model.pkl")

print("Model saved successfully!")