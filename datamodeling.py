"""
NYC Yellow Taxi - Machine Learning Model Training
Train fare prediction and tip classification models and save them for deployment.

Reads: NYC_YELLOW_TAXI_CLEAN.csv
Writes: fare_model.pkl, tip_model.pkl
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score


WORKSPACE_ROOT = "/Users/harish/FDM_EDA"
CLEAN_CSV = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_CLEAN.csv")
FARE_MODEL_PATH = os.path.join(WORKSPACE_ROOT, "fare_model.pkl")
TIP_MODEL_PATH = os.path.join(WORKSPACE_ROOT, "tip_model.pkl")


def load_and_prepare_data():
    """Load clean data and prepare features for modeling."""
    print("Loading data...")
    df = pd.read_csv(CLEAN_CSV)
    
    # Parse datetime and extract pickup hour
    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    
    # Define features
    features = ["trip_distance", "passenger_count", "trip_duration_min", "pickup_hour"]
    
    # Prepare targets
    y_fare = df["fare_amount"]
    y_tip = (df["tip_amount"] > 2).astype(int)
    
    # Drop rows with missing values in features or targets
    df_clean = df.dropna(subset=features + ["fare_amount", "tip_amount"])
    X = df_clean[features]
    y_fare = df_clean["fare_amount"]
    y_tip = (df_clean["tip_amount"] > 2).astype(int)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Features: {features}")
    
    return X, y_fare, y_tip, features


def train_fare_model(X, y_fare):
    """Train and optimize fare prediction model."""
    print("\n" + "="*60)
    print("TRAINING FARE PREDICTION MODEL (Regression)")
    print("="*60)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_fare, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train baseline models
    print("\n1. Training Linear Regression...")
    lr = LinearRegression().fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
    r2_lr = r2_score(y_test, y_pred_lr)
    print(f"   Linear Regression - RMSE: ${rmse_lr:.2f}, R²: {r2_lr:.4f}")
    
    print("\n2. Training Random Forest (baseline)...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    r2_rf = r2_score(y_test, y_pred_rf)
    print(f"   Random Forest - RMSE: ${rmse_rf:.2f}, R²: {r2_rf:.4f}")
    
    # Hyperparameter tuning
    print("\n3. Hyperparameter tuning with GridSearchCV...")
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [5, 10, None]
    }
    grid = GridSearchCV(
        RandomForestRegressor(random_state=42),
        param_grid,
        cv=3,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
        verbose=1
    )
    grid.fit(X_train, y_train)
    
    best_model = grid.best_estimator_
    y_pred_best = best_model.predict(X_test)
    rmse_best = np.sqrt(mean_squared_error(y_test, y_pred_best))
    r2_best = r2_score(y_test, y_pred_best)
    
    print(f"\n   Best parameters: {grid.best_params_}")
    print(f"   Optimized Random Forest - RMSE: ${rmse_best:.2f}, R²: {r2_best:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n   Feature Importance:")
    for _, row in feature_importance.iterrows():
        print(f"      {row['feature']}: {row['importance']:.4f}")
    
    return best_model, {
        'rmse': rmse_best,
        'r2': r2_best,
        'params': grid.best_params_
    }


def train_tip_model(X, y_tip):
    """Train and optimize tip classification model."""
    print("\n" + "="*60)
    print("TRAINING TIP PREDICTION MODEL (Classification)")
    print("="*60)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_tip, test_size=0.2, random_state=42
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"Class distribution (train): {y_train.value_counts().to_dict()}")
    
    # Train baseline models
    print("\n1. Training Logistic Regression...")
    clf = LogisticRegression(max_iter=1000, random_state=42).fit(X_train, y_train)
    y_pred_clf = clf.predict(X_test)
    acc_clf = accuracy_score(y_test, y_pred_clf)
    f1_clf = f1_score(y_test, y_pred_clf)
    print(f"   Logistic Regression - Accuracy: {acc_clf:.4f}, F1: {f1_clf:.4f}")
    
    print("\n2. Training Random Forest (baseline)...")
    rf_clf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X_train, y_train)
    y_pred_rf = rf_clf.predict(X_test)
    acc_rf = accuracy_score(y_test, y_pred_rf)
    f1_rf = f1_score(y_test, y_pred_rf)
    print(f"   Random Forest - Accuracy: {acc_rf:.4f}, F1: {f1_rf:.4f}")
    
    # Hyperparameter tuning
    print("\n3. Hyperparameter tuning with GridSearchCV...")
    param_grid_clf = {
        "n_estimators": [100, 200],
        "max_depth": [5, 10, None]
    }
    grid_clf = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid_clf,
        cv=3,
        scoring="f1",
        n_jobs=-1,
        verbose=1
    )
    grid_clf.fit(X_train, y_train)
    
    best_model = grid_clf.best_estimator_
    y_pred_best = best_model.predict(X_test)
    acc_best = accuracy_score(y_test, y_pred_best)
    f1_best = f1_score(y_test, y_pred_best)
    
    print(f"\n   Best parameters: {grid_clf.best_params_}")
    print(f"   Optimized Random Forest - Accuracy: {acc_best:.4f}, F1: {f1_best:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n   Feature Importance:")
    for _, row in feature_importance.iterrows():
        print(f"      {row['feature']}: {row['importance']:.4f}")
    
    return best_model, {
        'accuracy': acc_best,
        'f1': f1_best,
        'params': grid_clf.best_params_
    }


def save_models(fare_model, tip_model, fare_metrics, tip_metrics, features):
    """Save trained models and metadata to disk."""
    print("\n" + "="*60)
    print("SAVING MODELS")
    print("="*60)
    
    # Save fare model with metadata
    fare_bundle = {
        'model': fare_model,
        'features': features,
        'metrics': fare_metrics,
        'model_type': 'RandomForestRegressor'
    }
    joblib.dump(fare_bundle, FARE_MODEL_PATH)
    print(f"✓ Fare prediction model saved to: {FARE_MODEL_PATH}")
    
    # Save tip model with metadata
    tip_bundle = {
        'model': tip_model,
        'features': features,
        'metrics': tip_metrics,
        'model_type': 'RandomForestClassifier'
    }
    joblib.dump(tip_bundle, TIP_MODEL_PATH)
    print(f"✓ Tip prediction model saved to: {TIP_MODEL_PATH}")


def main():
    """Main training pipeline."""
    print("\n" + "="*60)
    print("NYC YELLOW TAXI - MODEL TRAINING PIPELINE")
    print("="*60)
    
    # Load and prepare data
    X, y_fare, y_tip, features = load_and_prepare_data()
    
    # Train fare prediction model
    fare_model, fare_metrics = train_fare_model(X, y_fare)
    
    # Train tip prediction model
    tip_model, tip_metrics = train_tip_model(X, y_tip)
    
    # Save models
    save_models(fare_model, tip_model, fare_metrics, tip_metrics, features)
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print("\nModel Summary:")
    print(f"  Fare Model: RMSE=${fare_metrics['rmse']:.2f}, R²={fare_metrics['r2']:.4f}")
    print(f"  Tip Model: Accuracy={tip_metrics['accuracy']:.4f}, F1={tip_metrics['f1']:.4f}")
    print("\nModels are ready for deployment in Streamlit app.")


if __name__ == "__main__":
    main()

