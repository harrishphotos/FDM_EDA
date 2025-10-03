import streamlit as st
import joblib
import numpy as np
import pandas as pd

# Load models with error handling
@st.cache_resource
def load_models():
    try:
        fare_model = joblib.load("streamlit_app/models/fare_model.pkl")
        tip_model = joblib.load("streamlit_app/models/tip_model.pkl")
        return fare_model, tip_model
    except FileNotFoundError as e:
        st.error(f"Model file not found: {e}")
        return None, None

fare_model, tip_model = load_models()

st.title("NYC Taxi Fare & Tip Prediction ")

# Input fields
col1, col2 = st.columns(2)

with col1:
    trip_distance = st.number_input("Trip Distance (miles)", min_value=0.1, step=0.1, value=5.0)
    passenger_count = st.number_input("Passenger Count", min_value=1, max_value=6, step=1, value=1)

with col2:
    trip_duration_min = st.number_input("Trip Duration (minutes)", min_value=1.0, step=0.5, value=15.0)
    pickup_hour = st.slider("Pickup Hour", 0, 23, 12)

# Check if models are loaded
if fare_model and tip_model:
    # Prepare features - make sure this matches your training data!
    features = np.array([[trip_distance, passenger_count, trip_duration_min, pickup_hour]])
    
    # Create two columns for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Predict Fare", use_container_width=True):
            try:
                fare = fare_model.predict(features)[0]
                st.success(f" Estimated Fare: ${fare:.2f}")
            except Exception as e:
                st.error(f"Prediction error: {e}")
    
    with col2:
        if st.button("Predict Tip Probability", use_container_width=True):
            try:
                tip_prob = tip_model.predict_proba(features)[0][1]
                st.success(f" Probability of Tip > $2: {tip_prob:.2%}")

                if tip_prob > 0.7:
                    st.info(" High chance of getting a good tip!")
                elif tip_prob > 0.4:
                    st.info(" Moderate chance of getting a tip")
                else:
                    st.info(" Lower probability of tip")
                    
            except Exception as e:
                st.error(f"Prediction error: {e}")
else:
    st.error("⚠️ Models could not be loaded. Please check the file paths.")
    st.info("Run `python Data_Engineering.py` first to train and save the models.")
