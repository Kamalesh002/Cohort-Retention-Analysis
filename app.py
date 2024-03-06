import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/image.html")
def image():
    return render_template("image.html")


@app.route("/reqline.html")
def result_form():
    return render_template("reqline.html")


@app.route("/result", methods=["POST"])
def result():
    # Get the user's input and convert to expected format
    cohort_year = request.form["cohort_year"]
    try:
        cohort_year = int(cohort_year)
    except ValueError:
        return "Invalid input: cohort year must be an integer"

    country = request.form["country"]

    # calculate retention for the given cohort year and country
    retention_data = calculate_retention(cohort_year, country)

    return render_template('result.html', retention_data=retention_data)


def calculate_retention(cohort_year, country):
    # Load the Online Retail II dataset
    df = pd.read_excel("online_retail_II.xlsx")

    # Convert the InvoiceDate column to a datetime format
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Filter the dataset by cohort year and country
    cohort_mask = (df['InvoiceDate'].dt.year == cohort_year) & (
        df['Country'] == country)
    cohort_df = df.loc[cohort_mask].copy()

    # Calculate the number of unique customers in the cohort
    cohort_customers = cohort_df['Customer ID'].nunique()

    # Calculate the retention rates for each month
    monthly_retention = []
    cohort_start_month = cohort_df['InvoiceDate'].dt.month.min()
    cohort_end_month = cohort_df['InvoiceDate'].dt.month.max()
    for month_offset in range(cohort_start_month, cohort_end_month + 1):
        # Calculate the number of customers in the current month
        current_month_df = cohort_df.loc[(
            cohort_df['InvoiceDate'].dt.month == month_offset)]
        current_month_customers = current_month_df['Customer ID'].nunique()

       # Calculate the retention rate for the current month
        retention_rate = (current_month_customers / cohort_customers)*100
        monthly_retention.append((month_offset, retention_rate))

    return monthly_retention


if __name__ == "__main__":
    app.run(debug=True)
