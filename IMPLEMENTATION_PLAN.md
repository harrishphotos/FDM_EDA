# Implementation Plan: EDA Visualizations & Prediction Interface

## Status Overview

### ✅ Already Implemented
- **Interactive Prediction Interface** - COMPLETE
  - Sidebar navigation with "Analytics Dashboard" and "Fare Prediction" pages
  - Input form with all required fields (pickup/dropoff zones, distance, duration, passengers, hour)
  - Model loading (`fare_model.pkl`, `tip_model.pkl`)
  - Real-time predictions with results display
  - Trip summary and financial estimates
  - See `PREDICTION_UI_GUIDE.md` for full details

### ⚠️ Needs Enhancement

Based on SOW requirements, the following EDA visualizations need to be expanded:

## Part 1: Enhanced EDA Visualizations in Dashboard

### Current State
The dashboard includes:
- ✅ Basic temporal analysis (monthly trends: trips, revenue, avg fare)
- ✅ Geospatial analysis (zone-level choropleth maps, hotspots, top zones)
- ✅ Flow analysis (origin-destination pairs, Sankey diagrams)
- ✅ Payment mix and rate code distributions
- ⚠️ **Missing**: Comprehensive temporal patterns (hourly, daily, seasonal)
- ⚠️ **Missing**: Financial/behavioral analysis (tip analysis by payment type, distance bins)
- ⚠️ **Missing**: Performance metrics display

### Required Enhancements

#### 1.1 Temporal Analysis Tab - EXPAND
**Objective**: Add hourly and day-of-week patterns as per SOW requirement for "hourly, daily, and seasonal demand patterns"

**Tasks**:
1. Add "Demand by Hour of Day" visualization
   - Line chart showing trip counts by hour (0-23)
   - Identify rush hour peaks and off-peak periods
   
2. Add "Demand by Day of Week" visualization
   - Bar chart showing trip counts by weekday
   - Highlight weekday vs weekend patterns
   
3. Add "Heatmap: Hour × Day of Week"
   - 2D heatmap showing trip density
   - Reveals peak hours on specific days

**Implementation**:
- Modify `tab_trends()` function in `streamlit_app/app.py`
- Use existing derived columns: `pickup_hour`, `pickup_dow`
- Create visualizations with Plotly Express

---

#### 1.2 Financial & Behavioral Analysis Tab - NEW
**Objective**: Investigate relationships between trip characteristics and tipping behavior (SOW requirement)

**Tasks**:
1. **Tip Analysis by Payment Type**
   - Compare average tip percentage for Credit vs Cash
   - Visualize "Do credit card payments yield better tips?"
   
2. **Fare Distribution Analysis**
   - Histogram of fare amounts
   - Box plots by borough or time of day
   
3. **Tip Percentage by Distance Bins**
   - Segment trips by distance (0-2, 2-5, 5-10, 10+ miles)
   - Show average tip % for each bin
   
4. **Trip Duration vs Fare Scatter**
   - Scatter plot with trendline
   - Identify fare-duration relationship

**Implementation**:
- Create new function `tab_financial_analysis(df)` in `streamlit_app/app.py`
- Add as new tab in `st.tabs()` array
- Use `tip_pct` derived column already present in data

---

#### 1.3 Performance Metrics Dashboard - NEW
**Objective**: Display model performance metrics prominently (addresses documentation gap)

**Tasks**:
1. Create new "Model Performance" tab or expander section
2. Display metrics:
   - **Fare Model**: RMSE, MAE, R² score
   - **Tip Model**: F1-score, ROC-AUC, Accuracy, Precision, Recall
3. Load metrics from saved file (e.g., `model_metrics.json`) or hardcode if unavailable

**Implementation**:
- Check if `Data Engineering.ipynb` contains final metrics
- If yes: Extract and save to `model_metrics.json`
- If no: Document this as critical gap
- Add metrics display in prediction page as expander or separate tab

---

## Part 2: Model Documentation Verification

### 2.1 Jupyter Notebook Audit
**Objective**: Verify `Data Engineering.ipynb` contains all required sections

**Tasks**:
1. Read notebook and check for:
   - ✅ Data cleaning and preprocessing
   - ⚠️ Comprehensive EDA (temporal, geospatial, financial)
   - ⚠️ Baseline model implementation (e.g., Linear Regression, Logistic Regression)
   - ⚠️ Advanced model implementation (Random Forest, XGBoost)
   - ⚠️ Model evaluation with metrics (RMSE, F1, ROC-AUC)
   - ⚠️ Hyperparameter tuning evidence
   - ⚠️ Feature importance or SHAP analysis

**Action Items**:
- If sections are missing: Add to notebook with proper documentation
- If sections exist but undocumented: Add markdown cells explaining each step
- Ensure reproducibility (all cells run in sequence)

---

### 2.2 Model Interpretability
**Objective**: Implement SHAP or feature importance analysis (SOW requirement)

**Tasks**:
1. Load trained models (`fare_model.pkl`, `tip_model.pkl`)
2. Generate feature importance plots
   - For Random Forest: Use `.feature_importances_`
   - Create bar chart showing top features
3. (Optional) Implement SHAP analysis
   - Install `shap` library
   - Generate SHAP summary plots
   - Explain top 3-5 features influencing predictions

**Implementation Location**:
- Add section to `Data Engineering.ipynb`
- Save plots as PNG files to `Docs/` folder
- Reference in final report

---

## Implementation Priority & Timeline

### High Priority (Complete by Oct 4)
1. ✅ **Prediction Interface** - ALREADY DONE
2. **Enhanced Temporal Analysis** - 2 hours
   - Add hourly and day-of-week charts to Trends tab
3. **Financial Analysis Tab** - 3 hours
   - Create new tab with tip and fare analysis
4. **Model Metrics Display** - 1 hour
   - Extract metrics from notebook or create placeholder

### Medium Priority (Complete by Oct 5)
5. **Notebook Audit** - 2 hours
   - Review and document all sections
6. **Feature Importance Analysis** - 2 hours
   - Generate and save plots

### Low Priority (If time permits)
7. SHAP analysis - 2 hours
8. Additional visualizations (optional enhancements)

---

## Deliverables Checklist

### Dashboard Enhancements
- [ ] Enhanced Trends tab with hourly/day-of-week patterns
- [ ] New Financial Analysis tab with tip analysis
- [ ] Model performance metrics display
- [ ] Updated screenshots for final report

### Documentation
- [ ] Verified `Data Engineering.ipynb` completeness
- [ ] Added feature importance section to notebook
- [ ] Created model metrics summary file
- [ ] Updated README if needed

---

## Testing Plan

### After Each Enhancement
1. Run Streamlit app: `streamlit run streamlit_app/app.py`
2. Navigate to modified tab
3. Verify visualizations render correctly
4. Test with filtered data (date range, borough filters)
5. Check responsiveness on different screen sizes

### Final Integration Test
1. Full walkthrough of all tabs
2. Test prediction interface with various inputs
3. Verify all data loads correctly
4. Confirm no errors in console/logs

---

## Notes

- The prediction interface is already fully implemented and functional
- Focus efforts on expanding EDA visualizations to meet SOW requirements
- Ensure all changes maintain existing functionality
- Document any assumptions or limitations in code comments
- Keep visualizations consistent with existing design (colors, fonts, layout)

## References
- SOW document: `Docs/Markdown/scope of work.md`
- Marking grid: `Docs/Markdown/FDM Mini Project-marking grid.md`
- Existing prediction guide: `PREDICTION_UI_GUIDE.md`
