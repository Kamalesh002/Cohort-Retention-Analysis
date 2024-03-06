import os
import pandas as pd
import numpy as np
# Data visualization
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns


def read_data(input_file="online_retail_II.xlsx"):
    """Reads raw data, computes total sales and clean column names"""
    # read file
    df = pd.read_excel(input_file)
    # clean column names
    df.columns = ['invoice_id', 'item_id', 'description', 'quantity', 'date',
                  'price', 'customer_id', 'country']
    # let's create the sales column
    df['sales'] = df['quantity'] * df['price']
    return df


def preprocess(input_file="online_retail_II.xlsx"):
    """Reads and preprocess data for cohort analysis"""
    # Read raw data, compute total sales and clean column names
    df = read_data(input_file)
    # remove customers with NA values
    df = df[~df.customer_id.isnull()]
    # convert the date to year-month format
    df['ym'] = df.date.dt.to_period('M')
    # Create an index column and merge it to the DataFrame
    ym_unique = df.ym.unique()
    unique_months = pd.DataFrame({
        "ym": ym_unique,
        "index": np.arange(ym_unique.shape[0])
    })
    unique_months.head()
    # merge ym and ym-index
    df = pd.merge(df, unique_months, how='inner', on='ym')
    # assings a cohort_id to each user based on the month they joined
    df["cohort_id"] = df.groupby("customer_id")['index'].transform("min")
    # create reverse mapping {"0": "2009-01", "1":"2010-01", ...}
    index_mapping = {row.index: row.ym for row in unique_months.itertuples()}
    # apply mapping to cohort_id (id when the customer joined)
    df['cohort_ym'] = df.cohort_id.map(index_mapping)
    # Difference between current index and cohort_id
    # number of months the user stayed as a customer
    df['cohort_index'] = df['index'] - df['cohort_id']
    return df, index_mapping


def compute_retention_rate(df, index_mapping):
    """computes retention rate given a dataframe preprocessed for cohort analysis"""
    # groupby cohort_id and cohort_index
    # count unique observations per customer
    agg_cohort = (
        df.groupby(['cohort_id', 'cohort_index'])
        ['customer_id']
        .nunique()
        .reset_index()
        .rename(columns={"customer_id": "nbr_customers"})
    )
    # convert to pivot table
    agg_cohort = agg_cohort.pivot_table(
        index='cohort_id', columns='cohort_index', values='nbr_customers')
    # set year-month in the index
    agg_cohort.index = agg_cohort.index.map(index_mapping)
    # vector of initial cohort size
    cohort_size = agg_cohort.iloc[:, 0]
    # compute percentages (retention rate)
    df_result = agg_cohort.divide(cohort_size, axis=0)
    return df_result


def plot_retention_rate(df_result):
    """Plots retention rate given a matrix with retention rates as a percentage"""
    # Initialize the figure
    plt.figure(figsize=(16, 10))
    # Adding a title
    plt.title('Retention Rate: Monthly Cohorts', fontsize=14)
    # Creating the seaborn based heatmap
    sns.heatmap(df_result, annot=True, fmt='.0%',
                cmap='Blues', vmin=0.0, vmax=0.6)
    plt.ylabel('Cohort Month')
    plt.xlabel('Cohort Index')
    plt.yticks(rotation='360')
    plt.show()


# Read data and preprocess it
# compute retention rate
df_results = compute_retention_rate(
    preprocess(input_file="online_retail_II.xlsx"))


# plot retention rate
plot_retention_rate(df_result)
