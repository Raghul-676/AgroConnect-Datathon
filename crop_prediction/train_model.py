import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
import joblib

# Load and preprocess the dataset
df = pd.read_csv("crop_data.csv")

# Columns
categorical_features = ["Crop", "SoilType", "Season", "IrrigationType"]
numerical_features = ["FieldSize"]
target_columns = ["ExpectedYield", "MarketPrice", "EstimatedRevenue"]

# Clean categorical columns (optional for consistency)
for col in categorical_features:
    df[col] = df[col].astype(str).str.lower().str.strip()

# Split features and target
X = df[categorical_features + numerical_features]
y = df[target_columns]

# Preprocessing
preprocessor = ColumnTransformer(transformers=[
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ("num", StandardScaler(), numerical_features)
])

# Full pipeline
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42)))
])

# Train the model
model.fit(X, y)

# Save the model
joblib.dump(model, "multi_output_crop_model.pkl")
print("✅ Model trained and saved as 'multi_output_crop_model.pkl'")
