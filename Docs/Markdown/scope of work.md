# Sri Lanka Institute of information Technology
## Fundamentals of Data Mining IT3051

### Mini-Project: Statement of Work Document
**2025**

**Weekend - 2.01: FDM_MLB_G07**

---

### Group Details

| IT Number  | Name              | Email                       | Contact Number |
| :--------- | :---------------- | :-------------------------- | :------------- |
| **IT23288744** | **Chamuditha H.V.C** | **it23288744@my.sliit.lk**  | **071 4366463**  |
| IT23291782 | Hariswara S       | it23291782@my.sliit.lk      | 0775577588     |
| IT23385900 | Ranasinghe I V L  | it23385900@my.sliit.lk      | 077 129 7010   |
| IT23232990 | Thennakoon S S H  | it23232990@my.sliit.lk      | 078 642 1227   |

**Submitted On: 2025-09-21**

---

## Table Of content
- **BACKGROUND** 3
- **SCOPE OF WORK** 5
- **ACTIVITIES** 6
- **APPROACH** 7
- **DELIVERABLES** 9
- **ASSUMPTIONS** 10
- **PROJECT PLAN & TIMELINE** 11
- **PROJECT TEAM, ROLES AND RESPONSIBILITIES** 12

---

## Background

In the highly competitive landscape of New York City, the transition to data-driven decision-making has become critical for the survival and success of the traditional taxi industry. While ride-hailing services have long utilized predictive analytics, individual taxi drivers are often left to navigate the city's complexities using only intuition and experience. This reliance on conventional methods in a digitally transformed sector creates a significant operational disadvantage.

The NYC Taxi & Limousine Commission (TLC) provides a massive, publicly available dataset containing millions of trip records.

This data holds the key to unlocking profound insights into traffic patterns, fare structures, and passenger behavior. However, for an individual driver or even the Taxi Union, this raw data is an untapped and inaccessible resource, leaving drivers to guess which routes are most profitable or when to anticipate a surge in demand. Conventional fare models, based simply on time and distance, fail to account for the complex variables—like time of day, passenger count, or specific locations—that truly influence a trip's profitability.

Predictive modeling offers a modern solution to this challenge. By applying machine learning algorithms to historical trip data, it is possible to uncover the hidden patterns that dictate fare amounts and tipping habits. This project will harness these techniques to build a system that translates vast, complex data into simple, actionable intelligence. By accurately forecasting fares and identifying the factors that lead to higher tips, we can provide drivers with a tool to move beyond guesswork and make strategic, data-informed decisions.

*   **Problem:** NYC taxi drivers face inconsistent earnings and operational inefficiencies because they lack access to data-driven insights. Traditional fare structures do not account for the many real-world variables that affect trip revenue, making it difficult for drivers to accurately predict their income and optimize their work strategies.
*   **Client:** The NYC Taxi Drivers' Union, representing independent yellow-cab drivers who face intense competition from large ride-hailing corporations (e.g., Uber, Lyft) whose advanced algorithms optimize pricing, routing, and driver incentives. To remain competitive and increase daily earnings, the union seeks data-driven tools and actionable insights that empower its members to make smarter decisions on pricing, location targeting, and time-of-day operations.
*   **Solution:** To develop a taxi trip prediction system that uses data mining and machine learning to accurately forecast fare amounts and the likelihood of high tips. By analyzing key trip-related factors, the system will provide drivers with the predictive insights needed to make more profitable decisions.
*   **Goal:** To create a reliable machine learning model and an interactive tool that can accurately forecast taxi fares and tipping behavior. The ultimate objective is to empower individual drivers with data-driven recommendations, helping them to optimize routes, manage their time effectively, and ultimately increase their profitability and service quality.
*   **Dataset (Selected and Approved):** We have chosen to construct a NYC Taxi Trip Dataset, which has over 100,000 trip data and is openly accessible, for this research. Time stamps, passenger counts, journey distances, fare amounts, tip amounts, payment methods, and pickup and drop-off locations are among the features included in the dataset. A solid basis for developing predictive models for fare prediction and tipping behavior is provided by this extensive dataset.

---

## Scope of Work

This project is focused on delivering a comprehensive data analysis and a prototype software solution based on a curated static **NYC Yellow Taxi Trip Data**. The scope is defined by the following boundaries to ensure timely and successful completion of the project objectives.

**The following activities are considered IN SCOPE for this project.**

1.  **Dataset Sourcing and Curation**
    *   Source raw monthly data files for the last three years (2023 – 2025/7) from nyc.gov.
    *   implement a stratified random-sampling strategy to combine these files into a single, manageable, and representative dataset.
    *   Target dataset size: approximately 100,000 rows.

2.  **Data Processing**
    *   Data preparation for the curated dataset, including cleaning, outlier treatment, and feature engineering (e.g., inflation adjustment for prices).

3.  **Exploratory Data Analysis**
    *   A comprehensive analysis focusing on temporal, geospatial, and financial patterns.

4.  **Predictive Modeling**
    *   The development and evaluation of two machine learning models:
        1.  Regression model for fare prediction.
        2.  Classification model for high-tip prediction.

5.  **Software Solution**
    *   The creation of a prototype web-based dashboard that includes EDA visualizations and an interactive prediction interface.

**Out of Scope**

1.  **Analysis of the Entire Multi-Year Dataset**
    *   The entire 3 year / ~33-month Dataset will contain Approx. 100 million rows.
    *   The analysis will be confined to the curated ~100,000 row sample, not the complete multi-million row dataset.

2.  **Real-Time System** - The project will not process live taxi data.

3.  **Cloud Deployment** - The solution will be developed to run locally.

---

## Activities

1.  **Dataset Sourcing, Curation, and Approval**
    *   Download the monthly NYC Yellow Taxi data files for the last three years from the official nyc.gov source.
    *   Develop and execute a Python script to perform stratified random sampling from these files to construct a representative master dataset of ~100,000 records.
    *   Formally submit the curated dataset and the sourcing methodology to the lab instructor for approval.

2.  **Data Quality Assurance, Cleaning and Preparation**
    *   Perform a deep audit of the dataset to identify and systematically address quality issues, including missing values, logical errors (e.g., negative fares), and extreme outliers.
    *   Engineer new, insightful features such as `trip_duration`, `hour_of_day`, `day_of_week`, and `tip_percentage` to enhance analysis.

3.  **Exploratory Data Analysis and Insight Generation**
    *   **Temporal Analysis:** Identify hourly, daily, and seasonal demand patterns to pinpoint city-wide rush hours, airport run peaks, and off-peak periods.
    *   **Geospatial Analysis:**
        *   Map high-value pickup and drop-off zones using geospatial heatmaps.
        *   Analyze trip flow between boroughs to identify the most lucrative routes and "hotspots."
    *   **Financial & Behavioral Analysis:** Investigate the relationships between trip distance, duration, payment type, and tip percentage to confirm or debunk common driver assumptions (e.g., "Do credit card payments yield better tips?").

4.  **Predictive Model Development**
    *   Build, train, and validate the fare prediction regression model.
    *   Build, train, and validate the high-tip classification model.
    *   Perform hyperparameter tuning and use cross-validation techniques to optimize the performance and robustness of each model.
    *   **Model Interpretation:** Analyze feature importance to understand why the models make certain predictions, extracting the key drivers behind fares and tips.

5.  **Software Solution and Interface Development**
    *   Design and develop a user-friendly web interface for the dashboard and integrate the trained machine learning models into the backend of the application to power the prediction features.
    *   Embed key EDA visualizations into the dashboard to provide users with contextual insights.

---

## Approach

1.  **Project Management & Version Control**
    *   All code and documentation will be managed using Git and hosted on a platform like GitHub to ensure collaboration and version tracking.

2.  **Data Preparation & Analysis**
    *   **Libraries**
        *   Pandas for data cleaning and transformation.
        *   NumPy for numerical operation.
        *   Matplotlib/Seaborn for static visualization.
        *   GeoPandas for geospatial mapping.
    *   **Geographical Analysis**
        *   Join the trip data with public NYC Taxi Zone Shapefile.
        *   Plot pickup density, average fares, and tip percentages by zone.
        *   Provides location-based context that is highly relevant for drivers and decision making.

3.  **Predictive Modeling**
    Our modeling strategy is grounded in a systematic, iterative approach to ensure robustness and interpretability.
    *   **Baseline Establishment**
        *   Begin with a simple baseline model (e.g., **Linear Regression** for fare prediction or **Logistic Regression** for tip classification).
        *   Serves as a benchmark to ensure any complex model provides a tangible improvement in performance.
    *   **Advanced Modeling**
        *   Progress to ensemble methods such as **Random Forest** and **XGBoost**, which are industry standards for tabular data.
        *   Capture complex non-linear relationships (e.g., interaction between time of day and pickup location on fare price).
    *   **Evaluation strategy**
        *   **Fare Regression Model:** Use Root Mean Squared Error (RMSE) to measure prediction error in dollars, providing directly interpretable results.
        *   **Tip Classification Model:** Focus on **F1-score** and **ROC-AUC score** to handle class imbalance (fewer high-tip trips) and evaluate model discrimination.
    *   **Interpretability**
        *   Employ techniques like **SHAP** (SHapley Additive exPlanations) or model feature importance plots.
        *   Explain which factors (e.g., trip duration, pickup location) most influence predictions, moving beyond a "black box" model and providing actionable insights for drivers.

4.  **Software Solution**
    The interactive dashboard will be developed as a web application using Python frameworks.
    *   **Frameworks:** We will use a lightweight framework such as **Streamlit** or **Flask** to build the application, allowing for rapid development of the interactive user interface.

---

## Deliverables

The following deliverables will be produced as part of the project outcome:

1.  **Cleaned and Processed Dataset**
    *   A refined dataset in CSV format, created from the original source. This dataset will have had missing values handled, outliers treated, and new features engineered, making it ready for modeling.

2.  **Exploratory Data Analysis (EDA) & Modeling Notebooks**
    *   A set of well-documented Jupyter Notebooks that provide a complete, reproducible record of the project's workflow, including data cleaning, the full exploratory analysis, and the model development process.

3.  **Predictive Machine Learning Models**
    *   The final, serialized versions of the trained regression model (for fare prediction) and classification model (for tip prediction), saved as pickle files.
    *   Documentation of each model's final performance metrics (RMSE for regression, F1-score and ROC-AUC for classification).

4.  **User-Friendly Web Application**
    *   A functional, standalone web application that serves as the primary user-facing deliverable.
    *   Features will include:
        *   An interactive form for users to input trip parameters (e.g., pickup/drop-off locations, time of day).
        *   Real-time predictions for the estimated fare and the probability of a high tip.
        *   A dashboard of key visualizations from the EDA that provide strategic insights.

5.  **Final Project Report and Documentation**
    *   A detailed written report covering background, scope, methodology, results, and conclusions.
    *   A brief user guide for operating the web application.

---

## Assumptions

To ensure the successful development and deployment of the NYC Yellow Taxi Fare and Analysis the following assumptions have been made:

1.  **Data Representativeness Assumption**
    *   The provided static dataset is assumed to be a sufficiently large and accurate sample that reflects the general operational patterns of the NYC taxi industry.

2.  **Data Field Integrity Assumption**
    *   It is assumed that the data fields are consistent and accurate. For instance, payment_type codes have a consistent meaning, and timestamps are recorded correctly, allowing for the reliable calculation of trip_duration.

3.  **Independence of Trips Assumption**
    *   Each record (trip) in the dataset is assumed to be an independent event, with no dependencies on other trips that could bias the model.

4.  **Location Data Mapping Assumption**
    *   We assume that the PULocationID and DOLocationID fields can be reliably and accurately mapped to meaningful geographical zones (e.g., boroughs, neighborhoods) using the publicly available NYC Taxi Zone lookup table.

5.  **No Major Unseen Variables Assumption**
    *   It is assumed that the primary factors influencing fares and tips (e.g., distance, time, location) are present in the dataset, and that there are no major hidden variables (e.g., city-wide events, weather) that significantly impact the outcomes.

6.  **Consistency of Data Distribution Assumption**
    *   The training and testing datasets are assumed to follow a similar distribution, ensuring that models trained on the training set can generalize effectively to unseen data.

---

## Project Plan & Timeline

*   **Planning & Strategy**
    *   Define scope and finalize SOW: **Week 9**
    *   Set Up Project Repository: **Week 9**
*   **Data Curation & Preprocessing**
    *   Dataset Sourcing & Sampling Script: **Week 9 - 10**
    *   Data Cleaning & Quality Assurance: **Week 10**
    *   Feature Engineering: **Week 10**
*   **Analysis & Modeling**
    *   Exploratory Data Analysis: **Week 11**
    *   Model Building (Baseline & Advanced): **Week 11 - 12**
    *   Model Evaluation & Tuning: **Week 12**
*   **Solution Development & Integration**
    *   Dashboard UI/UX Design: **Week 12**
    *   Backend Development & Model Integration: **Week 12 - 13**
    *   Frontend Development & Visualization: **Week 13**
*   **Finalization & Submission**
    *   Final Report Writing: **Week 14**
    *   Video Presentation Recording & Editing: **Week 14**
    *   Final Submission Package: **Week 14**

---

## Project Team, Roles and Responsibilities

| Member IT Number | Member Name | Member Role | Member Responsibilities |
| :--- | :--- | :--- | :--- |
| IT23288744 | Chamuditha H V C | Team Leader, <br> Solution Developer, <br> Data Analyst | - Coordinate team activities and ensure timely progress. <br> - Lead the initial data sourcing, sampling, and cleaning processes. <br> - Conduct foundational EDA (e.g., temporal, and univariate analysis). <br> - Contribute to documentation and report preparation. <br> - Oversee the final report compilation and ensure all deliverables are of high quality. |
| IT23291782 | Hariswara S | Data Analyst, <br> Backend Developer | - Lead the advanced, in-depth EDA, focusing on geospatial analysis and financial patterns. <br> - Take primary responsibility for feature engineering, including the inflation adjustment. <br> - Develop the backend of the web application. <br> - Develop Initial predictive and classifier models. |
| IT23385900 | Ranasinghe I V L | Machine Learning Engineer | - Lead the development, training, and hyperparameter tuning of both the fare prediction and tip classification models. <br> - Conduct rigorous model evaluation and comparison to select the best-performing algorithms. <br> - Analyze and interpret model results for the final report. <br> - Assist with the testing of the integrated models |
| IT23232990 | Thennakoon S S H | Frontend Developer <br> QA Specialist | - Lead the design and development of the user interface for the interactive dashboard. <br> - Integrate the EDA visualizations into the frontend to create an insightful user experience. <br> - Take primary responsibility for Quality Assurance (QA), including testing the predictive models and the final web application for bugs and usability. <br> - Lead preparation of project documentation and user guide. |