# generate_crop_model.py
# This script demonstrates how to train a simple machine learning model
# and save it as 'crop_model.pkl'.
# YOU NEED TO REPLACE THE DUMMY DATA AND MODEL TRAINING WITH YOUR ACTUAL DATA AND PROCESS.
# For the model to "process each crop according to their preferred conditions,"
# your training data MUST contain examples of these preferred conditions for each crop.

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle

print("Starting model generation script...")

# --- 1. Prepare Dummy Data (REPLACE THIS WITH YOUR ACTUAL DATASET) ---
# Your real data should have columns for:
# 'Nitrogen', 'Phosphorus', 'Potassium', 'Climate', 'Humidity', 'pH', 'Rainfall',
# 'Soil_Type', 'Topography', 'Water_Availability', 'Recommended_Crop'
#
# IMPORTANT: For the model to learn crop preferences, this dataset needs to be
# comprehensive and accurately reflect the optimal and suboptimal conditions
# for a wide variety of crops. Each row represents a set of conditions
# and the corresponding crop that thrives (or was grown) under those conditions.
# The more diverse and representative your data, the better the model will learn
# the "preferred conditions" for each crop.

# Full list of crops from model.py's CROP_CONDITIONS for consistent dummy data generation
all_crops = [
    'Rice', 'Wheat', 'Maize', 'Barley', 'Soybean', 'Alfalfa', 'Tomato', 'Potato', 'Coffee',
    'Banana', 'Coconut', 'Sugarcane for sugar or alcohol', 'Sunflower for oil seed',
    'Cotton (all varieties)', 'Orange', 'Apple', 'Grape', 'Tea', 'Tobacco',
    'Abaca (Manila hemp)', 'Almond', 'Apricot', 'Avocado', 'Beans, dry, edible, for grains',
    'Beet, sugar', 'Black pepper', 'Blueberry', 'Cabbage (red, white, Savoy)', 'Carrot, edible',
    'Cashew nuts', 'Cucumber', 'Dates', 'Eggplant', 'Garlic, dry', 'Ginger', 'Guava', 'Jute',
    'Lentil', 'Lettuce', 'Mango', 'Mushrooms', 'Mustard', 'Onion, dry', 'Papaya (pawpaw)',
    'Peach', 'Pineapple', 'Plum', 'Pumpkin, edible', 'Rhubarb', 'Rye', 'Safflower', 'Sesame',
    'Spinach', 'Strawberry', 'Sweet potato', 'Tangerine', 'Taro', 'Yam', 'Watermelon'
]

# Generate dummy data for 100 samples, cycling through the expanded crop list
num_samples = 100
np.random.seed(42) # for reproducibility

# Create base data points for each crop type
# This is a simplified way to create 'plausible' data for each crop
# In a real scenario, you'd use actual data or more sophisticated generation
base_conditions = {
    'Rice': {'N': 75, 'P': 45, 'K': 40, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.5, 'Rainfall': 200, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Wheat': {'N': 65, 'P': 30, 'K': 30, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 7.0, 'Rainfall': 75, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Maize': {'N': 85, 'P': 40, 'K': 40, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 120, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Barley': {'N': 55, 'P': 28, 'K': 28, 'Climate': 'Temperate', 'Humidity': 65, 'pH': 6.8, 'Rainfall': 90, 'Soil_Type': 'Loamy', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Soybean': {'N': 30, 'P': 55, 'K': 45, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 150, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Alfalfa': {'N': 10, 'P': 60, 'K': 75, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 7.0, 'Rainfall': 100, 'Soil_Type': 'Silty', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Tomato': {'N': 80, 'P': 60, 'K': 115, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.4, 'Rainfall': 90, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Potato': {'N': 100, 'P': 70, 'K': 140, 'Climate': 'Temperate', 'Humidity': 78, 'pH': 6.0, 'Rainfall': 115, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Coffee': {'N': 100, 'P': 30, 'K': 100, 'Climate': 'Tropical', 'Humidity': 82, 'pH': 6.2, 'Rainfall': 200, 'Soil_Type': 'Clayey', 'Topography': 'Sloped', 'Water_Availability': 'High'},
    'Banana': {'N': 125, 'P': 40, 'K': 175, 'Climate': 'Tropical', 'Humidity': 88, 'pH': 6.5, 'Rainfall': 250, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Coconut': {'N': 65, 'P': 30, 'K': 125, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.5, 'Rainfall': 150, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Sugarcane for sugar or alcohol': {'N': 125, 'P': 50, 'K': 150, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 200, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Sunflower for oil seed': {'N': 65, 'P': 40, 'K': 80, 'Climate': 'Temperate', 'Humidity': 50, 'pH': 6.8, 'Rainfall': 75, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Cotton (all varieties)': {'N': 100, 'P': 45, 'K': 80, 'Climate': 'Tropical', 'Humidity': 60, 'pH': 6.5, 'Rainfall': 110, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Orange': {'N': 75, 'P': 30, 'K': 65, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 115, 'Soil_Type': 'Loamy', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Apple': {'N': 55, 'P': 25, 'K': 75, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 115, 'Soil_Type': 'Loamy', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Grape': {'N': 45, 'P': 22, 'K': 55, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.5, 'Rainfall': 60, 'Soil_Type': 'Sandy', 'Topography': 'Sloped', 'Water_Availability': 'Low'},
    'Tea': {'N': 100, 'P': 30, 'K': 65, 'Climate': 'Tropical', 'Humidity': 88, 'pH': 5.0, 'Rainfall': 275, 'Soil_Type': 'Silty', 'Topography': 'Hilly', 'Water_Availability': 'High'},
    'Tobacco': {'N': 55, 'P': 40, 'K': 75, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.0, 'Rainfall': 90, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Abaca (Manila hemp)': {'N': 65, 'P': 30, 'K': 85, 'Climate': 'Tropical', 'Humidity': 82, 'pH': 6.5, 'Rainfall': 200, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Almond': {'N': 50, 'P': 22, 'K': 40, 'Climate': 'Arid', 'Humidity': 40, 'pH': 7.2, 'Rainfall': 45, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Low'},
    'Apricot': {'N': 40, 'P': 18, 'K': 30, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.5, 'Rainfall': 75, 'Soil_Type': 'Loamy', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Avocado': {'N': 75, 'P': 30, 'K': 65, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 150, 'Soil_Type': 'Silty', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Beans, dry, edible, for grains': {'N': 30, 'P': 45, 'K': 40, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.5, 'Rainfall': 90, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Beet, sugar': {'N': 100, 'P': 55, 'K': 100, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.8, 'Rainfall': 75, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Black pepper': {'N': 85, 'P': 40, 'K': 100, 'Climate': 'Tropical', 'Humidity': 88, 'pH': 6.0, 'Rainfall': 250, 'Soil_Type': 'Clayey', 'Topography': 'Sloped', 'Water_Availability': 'High'},
    'Blueberry': {'N': 30, 'P': 15, 'K': 30, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 5.0, 'Rainfall': 115, 'Soil_Type': 'Peaty', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Cabbage (red, white, Savoy)': {'N': 100, 'P': 45, 'K': 80, 'Climate': 'Temperate', 'Humidity': 80, 'pH': 6.8, 'Rainfall': 90, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Carrot, edible': {'N': 55, 'P': 30, 'K': 65, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 75, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Cashew nuts': {'N': 45, 'P': 18, 'K': 55, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 5.8, 'Rainfall': 150, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Cucumber': {'N': 75, 'P': 40, 'K': 85, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.5, 'Rainfall': 115, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Dates': {'N': 40, 'P': 15, 'K': 50, 'Climate': 'Arid', 'Humidity': 30, 'pH': 7.8, 'Rainfall': 10, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Low'},
    'Eggplant': {'N': 65, 'P': 30, 'K': 75, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 100, 'Soil_Type': 'Silty', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Garlic, dry': {'N': 50, 'P': 25, 'K': 40, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.8, 'Rainfall': 60, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Ginger': {'N': 75, 'P': 40, 'K': 85, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.2, 'Rainfall': 200, 'Soil_Type': 'Silty', 'Topography': 'Hilly', 'Water_Availability': 'High'},
    'Guava': {'N': 65, 'P': 30, 'K': 75, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.0, 'Rainfall': 115, 'Soil_Type': 'Loamy', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Jute': {'N': 55, 'P': 25, 'K': 40, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.5, 'Rainfall': 200, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Lentil': {'N': 15, 'P': 30, 'K': 25, 'Climate': 'Temperate', 'Humidity': 50, 'pH': 6.8, 'Rainfall': 50, 'Soil_Type': 'Silty', 'Topography': 'Flat', 'Water_Availability': 'Low'},
    'Lettuce': {'N': 65, 'P': 30, 'K': 50, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 75, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Mango': {'N': 75, 'P': 30, 'K': 85, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.2, 'Rainfall': 150, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Mushrooms': {'N': 0, 'P': 0, 'K': 0, 'Climate': 'Temperate', 'Humidity': 95, 'pH': 6.5, 'Rainfall': 0, 'Soil_Type': 'Peaty', 'Topography': 'Flat', 'Water_Availability': 'High'}, # Special case
    'Mustard': {'N': 55, 'P': 30, 'K': 40, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.8, 'Rainfall': 60, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Onion, dry': {'N': 75, 'P': 40, 'K': 65, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 60, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Papaya (pawpaw)': {'N': 100, 'P': 40, 'K': 125, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.5, 'Rainfall': 200, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Peach': {'N': 55, 'P': 25, 'K': 65, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.5, 'Rainfall': 90, 'Soil_Type': 'Loamy', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Pineapple': {'N': 65, 'P': 30, 'K': 85, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 5.2, 'Rainfall': 150, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Plum': {'N': 50, 'P': 22, 'K': 40, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.5, 'Rainfall': 75, 'Soil_Type': 'Clayey', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Pumpkin, edible': {'N': 75, 'P': 40, 'K': 85, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 90, 'Soil_Type': 'Silty', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Rhubarb': {'N': 65, 'P': 30, 'K': 50, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.0, 'Rainfall': 100, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Rye': {'N': 55, 'P': 28, 'K': 30, 'Climate': 'Temperate', 'Humidity': 60, 'pH': 6.0, 'Rainfall': 60, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Low'},
    'Safflower': {'N': 40, 'P': 22, 'K': 30, 'Climate': 'Arid', 'Humidity': 40, 'pH': 7.0, 'Rainfall': 35, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Low'},
    'Sesame': {'N': 50, 'P': 25, 'K': 40, 'Climate': 'Tropical', 'Humidity': 60, 'pH': 6.8, 'Rainfall': 75, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Spinach': {'N': 65, 'P': 30, 'K': 50, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.8, 'Rainfall': 75, 'Soil_Type': 'Silty', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Strawberry': {'N': 55, 'P': 30, 'K': 65, 'Climate': 'Temperate', 'Humidity': 70, 'pH': 6.0, 'Rainfall': 90, 'Soil_Type': 'Loamy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Sweet potato': {'N': 45, 'P': 30, 'K': 100, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.0, 'Rainfall': 150, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
    'Tangerine': {'N': 65, 'P': 30, 'K': 55, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 115, 'Soil_Type': 'Loamy', 'Topography': 'Sloped', 'Water_Availability': 'Medium'},
    'Taro': {'N': 75, 'P': 40, 'K': 85, 'Climate': 'Tropical', 'Humidity': 88, 'pH': 6.0, 'Rainfall': 250, 'Soil_Type': 'Clayey', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Yam': {'N': 65, 'P': 30, 'K': 75, 'Climate': 'Tropical', 'Humidity': 80, 'pH': 6.0, 'Rainfall': 150, 'Soil_Type': 'Silty', 'Topography': 'Flat', 'Water_Availability': 'High'},
    'Watermelon': {'N': 75, 'P': 40, 'K': 85, 'Climate': 'Tropical', 'Humidity': 70, 'pH': 6.5, 'Rainfall': 90, 'Soil_Type': 'Sandy', 'Topography': 'Flat', 'Water_Availability': 'Medium'},
}

# Create lists to hold the data for the DataFrame
nitrogen_data = []
phosphorus_data = []
potassium_data = []
climate_data = []
humidity_data = []
ph_data = []
rainfall_data = []
soil_type_data = []
topography_data = []
water_availability_data = []
recommended_crop_data = []

# Populate the lists by cycling through the crops and adding some noise
for i in range(num_samples):
    crop_name = all_crops[i % len(all_crops)] # Cycle through all crops
    base = base_conditions[crop_name]

    # Add some random noise to numerical features
    nitrogen_data.append(max(0, base['N'] + np.random.randint(-10, 10)))
    phosphorus_data.append(max(0, base['P'] + np.random.randint(-5, 5)))
    potassium_data.append(max(0, base['K'] + np.random.randint(-10, 10)))
    humidity_data.append(max(0, min(100, base['Humidity'] + np.random.randint(-5, 5))))
    ph_data.append(max(0.0, min(14.0, round(base['pH'] + np.random.uniform(-0.5, 0.5), 1))))
    rainfall_data.append(max(0, base['Rainfall'] + np.random.randint(-20, 20)))

    # Categorical features remain the same for simplicity or can be varied if needed
    climate_data.append(base['Climate'])
    soil_type_data.append(np.random.choice(base['Soil_Type']) if isinstance(base['Soil_Type'], list) else base['Soil_Type'])
    topography_data.append(base['Topography'])
    water_availability_data.append(base['Water_Availability'])
    recommended_crop_data.append(crop_name)

data = {
    'Nitrogen': nitrogen_data,
    'Phosphorus': phosphorus_data,
    'Potassium': potassium_data,
    'Climate': climate_data,
    'Humidity': humidity_data,
    'pH': ph_data,
    'Rainfall': rainfall_data,
    'Soil_Type': soil_type_data,
    'Topography': topography_data,
    'Water_Availability': water_availability_data,
    'Recommended_Crop': recommended_crop_data,
}

df = pd.DataFrame(data)

# Define features (X) and target (y)
X = df[['Nitrogen', 'Phosphorus', 'Potassium', 'Climate', 'Humidity', 'pH', 'Rainfall',
        'Soil_Type', 'Topography', 'Water_Availability']]
y = df['Recommended_Crop']

# Identify categorical and numerical features
categorical_features = ['Climate', 'Soil_Type', 'Topography', 'Water_Availability']
numerical_features = ['Nitrogen', 'Phosphorus', 'Potassium', 'Humidity', 'pH', 'Rainfall']

# Create a column transformer for preprocessing
# This will apply OneHotEncoder to categorical features and pass numerical features through
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('num', 'passthrough', numerical_features)
    ])

# --- 2. Train a Machine Learning Model (REPLACE RandomForestClassifier if needed) ---
# Create a pipeline that first preprocesses the data and then trains the model
model_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('classifier', RandomForestClassifier(random_state=42))])

# Split data into training and testing sets (optional, but good practice)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
print("Training the model...")
model_pipeline.fit(X_train, y_train)
print("Model training complete.")

# Evaluate the model (optional)
accuracy = model_pipeline.score(X_test, y_test)
print(f"Model accuracy on test set: {accuracy:.2f}")

# --- 3. Save the Trained Model and Preprocessor ---
# It's best practice to save the entire pipeline, including the preprocessor,
# so that when you load the model, it knows how to transform new data.
model_filename = 'crop_model.pkl'
try:
    with open(model_filename, 'wb') as file:
        pickle.dump(model_pipeline, file)
    print(f"Model saved successfully as '{model_filename}'")
except Exception as e:
    print(f"Error saving model: {e}")

print("Script finished.")
