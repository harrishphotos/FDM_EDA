"""
Prediction tabs for fare and tip prediction using trained ML models.
"""

import os
import joblib
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Get workspace root dynamically (works both locally and on Streamlit Cloud)
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FARE_MODEL_PATH = os.path.join(WORKSPACE_ROOT, "fare_model.pkl")
TIP_MODEL_PATH = os.path.join(WORKSPACE_ROOT, "tip_model.pkl")


@st.cache_resource(show_spinner=False)
def load_models():
    """Load pre-trained models from disk."""
    try:
        fare_bundle = joblib.load(FARE_MODEL_PATH)
        tip_bundle = joblib.load(TIP_MODEL_PATH)
        return fare_bundle, tip_bundle
    except FileNotFoundError:
        return None, None


def render_fare_prediction(df: pd.DataFrame) -> None:
    """Render the fare prediction tab."""
    st.markdown("""
    ### 💰 Fare Amount Prediction
    
    Use our machine learning model to predict taxi fares based on trip characteristics.
    This **Random Forest** model achieves **77% accuracy** (R² = 0.77) on test data.
    """)
    
    with st.expander("ℹ️ Why Random Forest? (vs Linear Regression)"):
        st.markdown("""
        Random Forest was chosen because it **outperforms linear models** by 8%:
        
        - **Linear Regression**: RMSE $10.08 (assumes straight-line relationship)
        - **Random Forest**: RMSE $9.23 (captures complex patterns)
        
        **Key Advantages:**
        - Handles non-linear pricing (rush hour surcharges, distance tiers)
        - Learns feature interactions automatically
        - More accurate predictions for drivers
        """)
    
    fare_bundle, _ = load_models()
    
    if fare_bundle is None:
        st.error("⚠️ Fare prediction model not found. Please run `datamodeling.py` to train the models.")
        return
    
    fare_model = fare_bundle['model']
    fare_metrics = fare_bundle['metrics']
    
    # Display model performance
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Prediction Error (RMSE)", f"${fare_metrics['rmse']:.2f}", help="Root Mean Squared Error - average prediction error in dollars")
    col2.metric("R² Score", f"{fare_metrics['r2']:.4f}", help="Model explains 77% of fare variation")
    col3.metric("Model Type", "Random Forest", help="Optimized with 200 trees, max depth 5")
    
    st.markdown("---")
    
    # Prediction interface
    st.subheader("🎯 Predict a New Fare")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trip_distance = st.number_input(
            "Trip Distance (miles)",
            min_value=0.0,
            max_value=200.0,
            value=5.0,
            step=0.1,
            help="Distance of the trip in miles"
        )
        
        passenger_count = st.number_input(
            "Passenger Count",
            min_value=1,
            max_value=6,
            value=1,
            step=1,
            help="Number of passengers"
        )
    
    with col2:
        trip_duration_min = st.number_input(
            "Trip Duration (minutes)",
            min_value=1.0,
            max_value=1440.0,
            value=15.0,
            step=1.0,
            help="Expected trip duration in minutes"
        )
        
        pickup_hour = st.slider(
            "Pickup Hour",
            min_value=0,
            max_value=23,
            value=12,
            format="%d:00",
            help="Hour of the day (0 = 12 AM, 12 = 12 PM, 23 = 11 PM)"
        )
        st.caption(f"Selected: {pickup_hour % 12 or 12} {'AM' if pickup_hour < 12 else 'PM'}")
    
    # Make prediction
    if st.button("🚀 Predict Fare", type="primary"):
        input_data = pd.DataFrame({
            'trip_distance': [trip_distance],
            'passenger_count': [passenger_count],
            'trip_duration_min': [trip_duration_min],
            'pickup_hour': [pickup_hour]
        })
        
        predicted_fare = fare_model.predict(input_data)[0]
        
        st.success(f"### Predicted Fare: **${predicted_fare:.2f}**")
        
        # Show similar trips
        st.markdown("---")
        st.subheader("📊 Similar Trips in Dataset")
        
        similar_trips = df[
            (df['trip_distance'].between(trip_distance * 0.8, trip_distance * 1.2)) &
            (df['trip_duration_min'].between(trip_duration_min * 0.8, trip_duration_min * 1.2))
        ].copy()
        
        if len(similar_trips) > 0:
            st.write(f"Found {len(similar_trips)} similar trips in the dataset")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Actual Fare", f"${similar_trips['fare_amount'].mean():.2f}")
            col2.metric("Min Fare", f"${similar_trips['fare_amount'].min():.2f}")
            col3.metric("Max Fare", f"${similar_trips['fare_amount'].max():.2f}")
            
            # Distribution plot
            fig = px.histogram(
                similar_trips,
                x='fare_amount',
                nbins=30,
                title="Fare Distribution for Similar Trips",
                labels={'fare_amount': 'Fare Amount ($)'}
            )
            fig.add_vline(
                x=predicted_fare,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Predicted: ${predicted_fare:.2f}",
                annotation_position="top"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No similar trips found in the dataset with these characteristics.")
    
    # Feature importance
    st.markdown("---")
    st.subheader("📈 Model Insights")
    
    feature_importance = pd.DataFrame({
        'Feature': ['Trip Distance', 'Trip Duration', 'Passenger Count', 'Pickup Hour'],
        'Importance': fare_model.feature_importances_
    }).sort_values('Importance', ascending=True)
    
    fig = px.bar(
        feature_importance,
        y='Feature',
        x='Importance',
        orientation='h',
        title="Feature Importance for Fare Prediction",
        color='Importance',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **💡 Key Insights:**
    - **Trip distance** is the strongest predictor of fare amount (85% importance)
    - **Trip duration** accounts for temporal factors (14% importance)
    - **Passenger count** and **pickup hour** have minimal impact on base fare
    """)


def render_tip_prediction(df: pd.DataFrame) -> None:
    """Render the tip prediction tab."""
    st.markdown("""
    ### 💵 Tip Likelihood Prediction
    
    Predict whether a trip will receive a **tip greater than $2** using our classification model.
    This **Random Forest** model achieves **66.5% accuracy** and **F1-score of 0.78** on test data.
    """)
    
    with st.expander("ℹ️ Why Random Forest? (vs Logistic Regression)"):
        st.markdown("""
        Random Forest was chosen for better tip prediction:
        
        - **Logistic Regression**: F1 0.7769 (assumes linear decision boundary)
        - **Random Forest**: F1 0.7847 (captures complex tipping patterns)
        
        **Key Advantages:**
        - Captures non-linear tipping behavior (time of day effects, trip length thresholds)
        - Handles payment method and route type interactions
        - Better at identifying high-tip probability trips
        """)
    
    _, tip_bundle = load_models()
    
    if tip_bundle is None:
        st.error("⚠️ Tip prediction model not found. Please run `datamodeling.py` to train the models.")
        return
    
    tip_model = tip_bundle['model']
    tip_metrics = tip_bundle['metrics']
    
    # Display model performance
    col1, col2, col3 = st.columns(3)
    col1.metric("Model Accuracy", f"{tip_metrics['accuracy']:.2%}", help="Correct predictions out of all predictions")
    col2.metric("F1-Score", f"{tip_metrics['f1']:.4f}", help="Balanced measure of precision and recall (0-1 scale)")
    col3.metric("Model Type", "Random Forest", help="Optimized with 100 trees, max depth 5")
    
    st.markdown("---")
    
    # Prediction interface
    st.subheader("🎯 Predict Tip Likelihood")
    
    col1, col2 = st.columns(2)
    
    with col1:
        trip_distance = st.number_input(
            "Trip Distance (miles)",
            min_value=0.0,
            max_value=200.0,
            value=3.0,
            step=0.1,
            key="tip_distance",
            help="Distance of the trip in miles"
        )
        
        passenger_count = st.number_input(
            "Passenger Count",
            min_value=1,
            max_value=6,
            value=1,
            step=1,
            key="tip_passengers",
            help="Number of passengers"
        )
    
    with col2:
        trip_duration_min = st.number_input(
            "Trip Duration (minutes)",
            min_value=1.0,
            max_value=1440.0,
            value=10.0,
            step=1.0,
            key="tip_duration",
            help="Expected trip duration in minutes"
        )
        
        pickup_hour = st.slider(
            "Pickup Hour",
            min_value=0,
            max_value=23,
            value=18,
            format="%d:00",
            key="tip_hour",
            help="Hour of the day (0 = 12 AM, 12 = 12 PM, 23 = 11 PM)"
        )
        st.caption(f"Selected: {pickup_hour % 12 or 12} {'AM' if pickup_hour < 12 else 'PM'}")
    
    # Make prediction
    if st.button("🚀 Predict Tip Likelihood", type="primary"):
        input_data = pd.DataFrame({
            'trip_distance': [trip_distance],
            'passenger_count': [passenger_count],
            'trip_duration_min': [trip_duration_min],
            'pickup_hour': [pickup_hour]
        })
        
        prediction = tip_model.predict(input_data)[0]
        probability = tip_model.predict_proba(input_data)[0]
        
        # Display result
        if prediction == 1:
            st.success("### ✅ Likely to receive a tip > $2")
            st.write(f"**Confidence:** {probability[1]:.1%}")
        else:
            st.warning("### ❌ Unlikely to receive a tip > $2")
            st.write(f"**Confidence:** {probability[0]:.1%}")
        
        # Probability gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=probability[1] * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Probability of Tip > $2"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen" if prediction == 1 else "orange"},
                'steps': [
                    {'range': [0, 33], 'color': "lightgray"},
                    {'range': [33, 66], 'color': "gray"},
                    {'range': [66, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        # Show similar trips
        st.markdown("---")
        st.subheader("📊 Similar Trips in Dataset")
        
        similar_trips = df[
            (df['trip_distance'].between(trip_distance * 0.8, trip_distance * 1.2)) &
            (df['trip_duration_min'].between(trip_duration_min * 0.8, trip_duration_min * 1.2))
        ].copy()
        
        if len(similar_trips) > 0:
            st.write(f"Found {len(similar_trips)} similar trips in the dataset")
            
            with_tip = (similar_trips['tip_amount'] > 2).sum()
            tip_rate = with_tip / len(similar_trips) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Trips with Tip > $2", str(with_tip))
            col2.metric("Tip Rate", f"{tip_rate:.1f}%")
            col3.metric("Avg Tip Amount", f"${similar_trips['tip_amount'].mean():.2f}")
            
            # Tip distribution
            fig = px.histogram(
                similar_trips,
                x='tip_amount',
                nbins=30,
                title="Tip Distribution for Similar Trips",
                labels={'tip_amount': 'Tip Amount ($)'}
            )
            fig.add_vline(
                x=2.0,
                line_dash="dash",
                line_color="red",
                annotation_text="$2 Threshold",
                annotation_position="top"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No similar trips found in the dataset with these characteristics.")
    
    # Feature importance
    st.markdown("---")
    st.subheader("📈 Model Insights")
    
    feature_importance = pd.DataFrame({
        'Feature': ['Trip Distance', 'Trip Duration', 'Passenger Count', 'Pickup Hour'],
        'Importance': tip_model.feature_importances_
    }).sort_values('Importance', ascending=True)
    
    fig = px.bar(
        feature_importance,
        y='Feature',
        x='Importance',
        orientation='h',
        title="Feature Importance for Tip Prediction",
        color='Importance',
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **💡 Key Insights:**
    - **Trip duration** is the strongest predictor of tips (52% importance)
    - **Trip distance** also plays a significant role (39% importance)
    - **Pickup hour** affects tipping behavior - evening trips tend to have higher tips
    - **Payment method matters:** Credit card payments are more likely to include tips
    """)
    
    # Hourly tip analysis
    st.markdown("---")
    st.subheader("🕐 Hourly Tip Analysis")
    
    hourly_tips = df.groupby('pickup_hour').agg({
        'tip_amount': 'mean',
        'VendorID': 'count'
    }).rename(columns={'VendorID': 'trip_count', 'tip_amount': 'avg_tip'}).reset_index()
    
    hourly_tips['tip_rate'] = df.groupby('pickup_hour').apply(
        lambda x: (x['tip_amount'] > 2).sum() / len(x) * 100
    ).values
    
    # Create readable time labels
    hourly_tips['hour_label'] = hourly_tips['pickup_hour'].apply(
        lambda h: f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"
    )
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(x=hourly_tips['hour_label'], y=hourly_tips['avg_tip'], name="Avg Tip ($)", marker_color='lightblue'),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=hourly_tips['hour_label'], y=hourly_tips['tip_rate'], name="Tip Rate (%)", mode='lines+markers', marker_color='red'),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Hour of Day")
    fig.update_yaxes(title_text="Average Tip Amount ($)", secondary_y=False)
    fig.update_yaxes(title_text="Tip Rate (% trips with tip > $2)", secondary_y=True)
    fig.update_layout(title_text="Average Tip and Tip Rate by Hour", xaxis_tickangle=-45)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Find best hours for tips
    best_hours = hourly_tips.nlargest(5, 'tip_rate')[['pickup_hour', 'hour_label', 'tip_rate', 'avg_tip']]
    st.markdown("**🌟 Best Hours for Tips:**")
    for _, row in best_hours.iterrows():
        st.write(f"- **{row['hour_label']}**: {row['tip_rate']:.1f}% tip rate, ${row['avg_tip']:.2f} avg tip")

