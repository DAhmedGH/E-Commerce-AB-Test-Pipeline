# E-Commerce A/B Testing & Analytics Pipeline

## Project Overview
This project is an end-to-end data analytics pipeline designed to evaluate a new e-commerce checkout flow. I simulated realistic raw event logs, transformed the data in the cloud using dbt and Google BigQuery, conducted statistical hypothesis testing in Python, and visualized the business impact in an interactive Tableau dashboard.

**[View the Interactive Tableau Dashboard Here](https://public.tableau.com/app/profile/danieal.ahmed/viz/E-CommerceCheckoutABTest/Dashboard1)**

## Tools Used
* **Python (Pandas, NumPy, SciPy, Statsmodels):** Raw data generation and statistical hypothesis testing (Z-tests, T-tests).
* **Google BigQuery:** Cloud data warehousing and raw event storage.
* **dbt (Data Build Tool) & SQL:** Analytics engineering and dimensional data modeling.
* **Tableau:** Data visualization and executive dashboard design.

## The Process
1. **Data Generation:** Used Python in a Jupyter Notebook to simulate 50,000 realistic user sessions with randomized device assignments, checkout events, and timestamped logs.
2. **Data Warehousing & Transformation:** Loaded the messy raw logs into Google BigQuery. Engineered a normalized data model using dbt to aggregate traffic, conversions, and revenue by variant group and device type.
3. **Statistical Analysis:** Queried the cleaned data back into Python to conduct rigorous hypothesis testing. Applied Two-proportion Z-tests for conversion rates and Welch's Two-Sample T-tests for Average Order Value (AOV) to prove statistical significance (95% confidence level).
4. **Data Visualization & Recommendation:** Built an executive-level dashboard in Tableau proving the Variant statistically outperformed the Control (14.3% vs 12.0% conversion, $55.05 vs $50.53 AOV). Provided a clear, data-driven recommendation to roll out the new checkout flow to 100% of users.