# model.py
# This script loads a pre-trained machine learning model pipeline (including preprocessor)
# and uses it to predict a crop. It now calculates compatibility for all crops
# and returns them as a JSON string, separated into compatible and incompatible lists.

import sys
import pickle
import numpy as np
import pandas as pd
import traceback
import json # Import json module

# --- Hardcoded Crop Preferred Conditions ---
# IMPORTANT: For a robust ML system, these conditions should primarily be learned
# by your model from a comprehensive training dataset. This dictionary is for
# illustrative purposes to show how you *could* incorporate explicit rules
# for validation or alternative suggestions.
#
# Ranges are inclusive. Categorical values must match exactly.
CROP_CONDITIONS = {
    'Rice': {
        'Nitrogen': (60, 90), 'Phosphorus': (30, 60), 'Potassium': (30, 60),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (6.0, 7.0),
        'Rainfall': (150, 250), 'Soil_Type': ['Clayey', 'Loamy'], 'Water_Availability': 'High',
    },
    'Wheat': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (20, 40),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.5),
        'Rainfall': (50, 100), 'Soil_Type': ['Loamy', 'Sandy', 'Silty'], 'Water_Availability': 'Medium',
    },
    'Maize': {
        'Nitrogen': (70, 100), 'Phosphorus': (30, 50), 'Potassium': (30, 50),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (80, 150), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'High',
    },
    'Barley': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 35), 'Potassium': (20, 35),
        'Climate': 'Temperate', 'Humidity': (55, 75), 'pH': (6.0, 7.5),
        'Rainfall': (60, 120), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Soybean': {
        'Nitrogen': (20, 40), 'Phosphorus': (40, 70), 'Potassium': (30, 60),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (100, 200), 'Soil_Type': ['Loamy', 'Clayey'], 'Water_Availability': 'High',
    },
    'Alfalfa': {
        'Nitrogen': (0, 20), 'Phosphorus': (40, 80), 'Potassium': (50, 100),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.5, 7.5),
        'Rainfall': (70, 140), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'Medium',
    },
    'Tomato': {
        'Nitrogen': (60, 100), 'Phosphorus': (40, 80), 'Potassium': (80, 150),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 6.8),
        'Rainfall': (60, 120), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Potato': {
        'Nitrogen': (80, 120), 'Phosphorus': (50, 90), 'Potassium': (100, 180),
        'Climate': 'Temperate', 'Humidity': (70, 85), 'pH': (5.5, 6.5),
        'Rainfall': (80, 150), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'High',
    },
    'Coffee': {
        'Nitrogen': (80, 120), 'Phosphorus': (20, 40), 'Potassium': (80, 120),
        'Climate': 'Tropical', 'Humidity': (75, 90), 'pH': (6.0, 6.5),
        'Rainfall': (150, 250), 'Soil_Type': ['Loamy', 'Clayey'], 'Water_Availability': 'High',
    },
    'Banana': {
        'Nitrogen': (100, 150), 'Phosphorus': (30, 50), 'Potassium': (150, 200),
        'Climate': 'Tropical', 'Humidity': (80, 95), 'pH': (6.0, 7.0),
        'Rainfall': (200, 300), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'High',
    },
    'Coconut': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (100, 150),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (6.0, 7.0),
        'Rainfall': (100, 200), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'High',
    },
    'Sugarcane for sugar or alcohol': {
        'Nitrogen': (100, 150), 'Phosphorus': (40, 60), 'Potassium': (120, 180),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (150, 250), 'Soil_Type': ['Clayey', 'Loamy'], 'Water_Availability': 'High',
    },
    'Sunflower for oil seed': {
        'Nitrogen': (50, 80), 'Phosphorus': (30, 50), 'Potassium': (60, 100),
        'Climate': 'Temperate', 'Humidity': (40, 60), 'pH': (6.0, 7.5),
        'Rainfall': (50, 100), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Cotton (all varieties)': {
        'Nitrogen': (80, 120), 'Phosphorus': (30, 60), 'Potassium': (60, 100),
        'Climate': 'Tropical', 'Humidity': (50, 70), 'pH': (6.0, 7.0),
        'Rainfall': (70, 150), 'Soil_Type': ['Clayey', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Orange': {
        'Nitrogen': (60, 90), 'Phosphorus': (20, 40), 'Potassium': (50, 80),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (80, 150), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Apple': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 30), 'Potassium': (60, 90),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (80, 150), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'Medium',
    },
    'Grape': {
        'Nitrogen': (30, 60), 'Phosphorus': (15, 30), 'Potassium': (40, 70),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.0),
        'Rainfall': (40, 80), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Low',
    },
    'Tea': {
        'Nitrogen': (80, 120), 'Phosphorus': (20, 40), 'Potassium': (50, 80),
        'Climate': 'Tropical', 'Humidity': (80, 95), 'pH': (4.5, 5.5), # Tea prefers acidic soil
        'Rainfall': (200, 350), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'High',
    },
    'Tobacco': {
        'Nitrogen': (40, 70), 'Phosphorus': (30, 50), 'Potassium': (60, 90),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (5.5, 6.5),
        'Rainfall': (60, 120), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Abaca (Manila hemp)': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (70, 100),
        'Climate': 'Tropical', 'Humidity': (75, 90), 'pH': (6.0, 7.0),
        'Rainfall': (150, 250), 'Soil_Type': ['Clayey', 'Loamy'], 'Water_Availability': 'High',
    },
    'Almond': {
        'Nitrogen': (40, 60), 'Phosphorus': (15, 30), 'Potassium': (30, 50),
        'Climate': 'Arid', 'Humidity': (30, 50), 'pH': (6.5, 8.0),
        'Rainfall': (30, 60), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Low',
    },
    'Apricot': {
        'Nitrogen': (30, 50), 'Phosphorus': (10, 25), 'Potassium': (20, 40),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.0),
        'Rainfall': (50, 100), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Avocado': {
        'Nitrogen': (60, 90), 'Phosphorus': (20, 40), 'Potassium': (50, 80),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (100, 200), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'High',
    },
    'Beans, dry, edible, for grains': {
        'Nitrogen': (20, 40), 'Phosphorus': (30, 60), 'Potassium': (30, 50),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.0),
        'Rainfall': (60, 120), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Beet, sugar': {
        'Nitrogen': (80, 120), 'Phosphorus': (40, 70), 'Potassium': (80, 120),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.5),
        'Rainfall': (50, 100), 'Soil_Type': ['Loamy', 'Clayey'], 'Water_Availability': 'Medium',
    },
    'Black pepper': {
        'Nitrogen': (70, 100), 'Phosphorus': (30, 50), 'Potassium': (80, 120),
        'Climate': 'Tropical', 'Humidity': (80, 95), 'pH': (5.5, 6.5),
        'Rainfall': (200, 300), 'Soil_Type': ['Loamy', 'Clayey'], 'Water_Availability': 'High',
    },
    'Blueberry': {
        'Nitrogen': (20, 40), 'Phosphorus': (10, 20), 'Potassium': (20, 40),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (4.5, 5.5), # Acidic soil
        'Rainfall': (80, 150), 'Soil_Type': ['Peaty', 'Sandy'], 'Water_Availability': 'High',
    },
    'Cabbage (red, white, Savoy)': {
        'Nitrogen': (80, 120), 'Phosphorus': (30, 60), 'Potassium': (60, 100),
        'Climate': 'Temperate', 'Humidity': (70, 90), 'pH': (6.0, 7.5),
        'Rainfall': (60, 120), 'Soil_Type': ['Loamy', 'Clayey'], 'Water_Availability': 'Medium',
    },
    'Carrot, edible': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 40), 'Potassium': (50, 80),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (50, 100), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Cashew nuts': {
        'Nitrogen': (30, 60), 'Phosphorus': (10, 25), 'Potassium': (40, 70),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (5.0, 6.5),
        'Rainfall': (100, 200), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Cucumber': {
        'Nitrogen': (60, 90), 'Phosphorus': (30, 50), 'Potassium': (70, 100),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (6.0, 7.0),
        'Rainfall': (80, 150), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'High',
    },
    'Dates': {
        'Nitrogen': (30, 50), 'Phosphorus': (10, 20), 'Potassium': (40, 60),
        'Climate': 'Arid', 'Humidity': (20, 40), 'pH': (7.0, 8.5),
        'Rainfall': (0, 20), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Low',
    },
    'Eggplant': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (60, 90),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (70, 140), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'Medium',
    },
    'Garlic, dry': {
        'Nitrogen': (40, 60), 'Phosphorus': (20, 30), 'Potassium': (30, 50),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.5),
        'Rainfall': (40, 80), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Ginger': {
        'Nitrogen': (60, 90), 'Phosphorus': (30, 50), 'Potassium': (70, 100),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (6.0, 6.5),
        'Rainfall': (150, 250), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'High',
    },
    'Guava': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (60, 90),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (5.0, 7.0),
        'Rainfall': (80, 150), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Jute': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 30), 'Potassium': (30, 50),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (6.0, 7.0),
        'Rainfall': (150, 250), 'Soil_Type': ['Clayey', 'Loamy'], 'Water_Availability': 'High',
    },
    'Lentil': {
        'Nitrogen': (10, 20), 'Phosphorus': (20, 40), 'Potassium': (20, 30),
        'Climate': 'Temperate', 'Humidity': (40, 60), 'pH': (6.0, 7.5),
        'Rainfall': (30, 70), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'Low',
    },
    'Lettuce': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (40, 60),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (50, 100), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Mango': {
        'Nitrogen': (60, 90), 'Phosphorus': (20, 40), 'Potassium': (70, 100),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (5.5, 7.0),
        'Rainfall': (100, 200), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Mushrooms': { # Conditions for growing medium, not soil
        'Nitrogen': (0, 0), 'Phosphorus': (0, 0), 'Potassium': (0, 0), # NPK not directly applicable to soil for mushrooms
        'Climate': 'Temperate', 'Humidity': (90, 100), 'pH': (6.0, 7.0), # High humidity, specific temperature
        'Rainfall': (0, 0), 'Soil_Type': ['Peaty'], 'Water_Availability': 'High', # Growing in substrate
    },
    'Mustard': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 40), 'Potassium': (30, 50),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.5),
        'Rainfall': (40, 80), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'Medium',
    },
    'Onion, dry': {
        'Nitrogen': (60, 90), 'Phosphorus': (30, 50), 'Potassium': (50, 80),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (40, 80), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Papaya (pawpaw)': {
        'Nitrogen': (80, 120), 'Phosphorus': (30, 50), 'Potassium': (100, 150),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (6.0, 7.0),
        'Rainfall': (150, 250), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'High',
    },
    'Peach': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 30), 'Potassium': (50, 80),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.0),
        'Rainfall': (60, 120), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Pineapple': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (70, 100),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (4.5, 6.0), # Prefers acidic
        'Rainfall': (100, 200), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Plum': {
        'Nitrogen': (40, 60), 'Phosphorus': (15, 30), 'Potassium': (30, 50),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (6.0, 7.0),
        'Rainfall': (50, 100), 'Soil_Type': ['Loamy', 'Clayey'], 'Water_Availability': 'Medium',
    },
    'Pumpkin, edible': {
        'Nitrogen': (60, 90), 'Phosphorus': (30, 50), 'Potassium': (70, 100),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (60, 120), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'Medium',
    },
    'Rhubarb': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (40, 60),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (5.5, 6.5),
        'Rainfall': (70, 140), 'Soil_Type': ['Loamy', 'Clayey'], 'Water_Availability': 'High',
    },
    'Rye': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 35), 'Potassium': (20, 40),
        'Climate': 'Temperate', 'Humidity': (50, 70), 'pH': (5.0, 7.0), # Tolerant to acidic
        'Rainfall': (40, 80), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Low',
    },
    'Safflower': {
        'Nitrogen': (30, 50), 'Phosphorus': (15, 30), 'Potassium': (20, 40),
        'Climate': 'Arid', 'Humidity': (30, 50), 'pH': (6.0, 8.0),
        'Rainfall': (20, 50), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Low',
    },
    'Sesame': {
        'Nitrogen': (40, 60), 'Phosphorus': (20, 30), 'Potassium': (30, 50),
        'Climate': 'Tropical', 'Humidity': (50, 70), 'pH': (6.0, 7.5),
        'Rainfall': (50, 100), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Spinach': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (40, 60),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (6.0, 7.5),
        'Rainfall': (50, 100), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'Medium',
    },
    'Strawberry': {
        'Nitrogen': (40, 70), 'Phosphorus': (20, 40), 'Potassium': (50, 80),
        'Climate': 'Temperate', 'Humidity': (60, 80), 'pH': (5.5, 6.5),
        'Rainfall': (60, 120), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Sweet potato': {
        'Nitrogen': (30, 60), 'Phosphorus': (20, 40), 'Potassium': (80, 120),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (5.5, 6.5),
        'Rainfall': (100, 200), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
    'Tangerine': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (40, 70),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (80, 150), 'Soil_Type': ['Loamy', 'Sandy'], 'Water_Availability': 'Medium',
    },
    'Taro': {
        'Nitrogen': (60, 90), 'Phosphorus': (30, 50), 'Potassium': (70, 100),
        'Climate': 'Tropical', 'Humidity': (80, 95), 'pH': (5.5, 6.5),
        'Rainfall': (200, 300), 'Soil_Type': ['Clayey', 'Loamy'], 'Water_Availability': 'High',
    },
    'Yam': {
        'Nitrogen': (50, 80), 'Phosphorus': (20, 40), 'Potassium': (60, 90),
        'Climate': 'Tropical', 'Humidity': (70, 90), 'pH': (5.5, 6.5),
        'Rainfall': (100, 200), 'Soil_Type': ['Loamy', 'Silty'], 'Water_Availability': 'High',
    },
    'Watermelon': {
        'Nitrogen': (60, 90), 'Phosphorus': (30, 50), 'Potassium': (70, 100),
        'Climate': 'Tropical', 'Humidity': (60, 80), 'pH': (6.0, 7.0),
        'Rainfall': (60, 120), 'Soil_Type': ['Sandy', 'Loamy'], 'Water_Availability': 'Medium',
    },
}

def calculate_compatibility(crop_name, features_dict):
    """
    Calculates a compatibility percentage for a given crop based on input features
    and the crop's preferred conditions.
    Returns a float (percentage).
    """
    preferred = CROP_CONDITIONS.get(crop_name)
    if not preferred:
        return 0.0 # No specific conditions defined, cannot calculate compatibility

    score = 0
    total_conditions = 0

    # Define the keys for numerical and categorical features
    numerical_keys = ['Nitrogen', 'Phosphorus', 'Potassium', 'Humidity', 'pH', 'Rainfall']
    categorical_keys = ['Climate', 'Soil_Type', 'Topography', 'Water_Availability']

    # Check numerical ranges
    for key in numerical_keys:
        if key in preferred and preferred[key] is not None:
            min_val, max_val = preferred[key]
            input_val = features_dict.get(key)
            if input_val is not None:
                total_conditions += 1
                if min_val <= input_val <= max_val:
                    score += 1
                # Optional: Add partial scoring for values close to the range
                # For simplicity, keeping it binary for now.

    # Check categorical values
    for key in categorical_keys:
        if key in preferred and preferred[key] is not None:
            preferred_val = preferred[key]
            input_val = features_dict.get(key)
            if input_val is not None:
                total_conditions += 1
                if isinstance(preferred_val, list):
                    if input_val in preferred_val:
                        score += 1
                else:
                    if input_val == preferred_val:
                        score += 1

    if total_conditions == 0:
        return 0.0 # Avoid division by zero if no conditions are defined

    compatibility_percentage = (score / total_conditions) * 100
    return compatibility_percentage

def get_suitable_crops(features_dict): # Removed threshold parameter
    """
    Calculates compatibility for all crops, separates them into compatible and incompatible,
    and returns a JSON string with sorted lists.
    """
    all_crops_data = []
    for crop_name in CROP_CONDITIONS.keys():
        compatibility = calculate_compatibility(crop_name, features_dict)
        all_crops_data.append({'crop': crop_name, 'compatibility': compatibility})

    compatible_crops = []
    incompatible_crops = []

    for item in all_crops_data:
        if item['compatibility'] > 0:
            compatible_crops.append(item)
        else:
            incompatible_crops.append(item)

    # Sort compatible crops by percentage in descending order
    compatible_crops.sort(key=lambda x: x['compatibility'], reverse=True)
    # Incompatible crops can remain unsorted or sorted alphabetically by name
    incompatible_crops.sort(key=lambda x: x['crop'])

    # Prepare the data structure for JSON output
    output_data = {
        'compatible_crops': compatible_crops,
        'incompatible_crops': incompatible_crops
    }

    return json.dumps(output_data) # Return JSON string

if __name__ == "__main__":
    # Expecting 11 arguments: script_name (sys.argv[0]) + 10 features
    if len(sys.argv) != 11:
        print("Usage: python model.py <N> <P> <K> <climate> <humidity> <ph> <rainfall> <soil_type> <topography> <water_availability>")
        sys.exit(1)

    try:
        nitrogen = float(sys.argv[1])
        phosphorus = float(sys.argv[2])
        potassium = float(sys.argv[3])
        climate_str = sys.argv[4]
        humidity = float(sys.argv[5])
        ph = float(sys.argv[6])
        rainfall = float(sys.argv[7])
        soil_type_str = sys.argv[8]
        topography_str = sys.argv[9]
        water_availability_str = sys.argv[10]

        input_features_raw = {
            'Nitrogen': nitrogen,
            'Phosphorus': phosphorus,
            'Potassium': potassium,
            'Climate': climate_str,
            'Humidity': humidity,
            'pH': ph,
            'Rainfall': rainfall,
            'Soil_Type': soil_type_str,
            'Topography': topography_str,
            'Water_Availability': water_availability_str
        }

        # Call the new function to get suitable crops based on compatibility
        # No threshold here, as all crops are returned, separated into compatible/incompatible
        result = get_suitable_crops(input_features_raw)
        print(result)

        # Optional: You can still load and use the ML model prediction internally
        # if you need it for other purposes, but it won't be printed as the main output.
        # try:
        #     with open('crop_model.pkl', 'rb') as model_file:
        #         ml_model_pipeline = pickle.load(model_file)
        #     input_df = pd.DataFrame([input_features_raw])
        #     ml_prediction = ml_model_pipeline.predict(input_df)[0]
        #     # You can use ml_prediction here for internal logic or logging
        # except FileNotFoundError:
        #     pass # Handle if model file is not found
        # except Exception as e:
        #     pass # Handle other ML model loading/prediction errors


    except ValueError:
        print("Error: All numerical inputs must be valid numbers. Check your form inputs.")
        sys.exit(1)
    except IndexError:
        print("Error: Missing command-line arguments. Please provide all required inputs. Expected 10 arguments, received " + str(len(sys.argv) - 1))
        sys.exit(1)
    except Exception as e:
        error_info = traceback.format_exc()
        print(f"An unexpected error occurred in main execution: {e}\nTraceback:\n{error_info}")
        sys.exit(1)

