# -*- coding: utf-8 -*-
"""Retail_Data_Pipeline.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PulhyJ5vRddy3GAYZwr_AtcoD52Q8dQU

Walmart is the biggest retail store in the United States. Just like others, they have been expanding their e-commerce part of the business. By the end of 2022, e-commerce represented a roaring $80 billion in sales, which is 13% of total sales of Walmart. One of the main factors that affects their sales is public holidays, like the Super Bowl, Labour Day, Thanksgiving, and Christmas.

In this project, you have been tasked with creating a data pipeline for the analysis of supply and demand around the holidays, along with conducting a preliminary analysis of the data. You will be working with two data sources: grocery sales and complementary data. You have been provided with the `grocery_sales` table in `PostgreSQL` database with the following features:

# `grocery_sales`
- `"index"` - unique ID of the row
- `"Store_ID"` - the store number
- `"Date"` - the week of sales
- `"Weekly_Sales"` - sales for the given store

Also, you have the `extra_data.parquet` file that contains complementary data:

# `extra_data.parquet`
- `"IsHoliday"` - Whether the week contains a public holiday - 1 if yes, 0 if no.
- `"Temperature"` - Temperature on the day of sale
- `"Fuel_Price"` - Cost of fuel in the region
- `"CPI"` – Prevailing consumer price index
- `"Unemployment"` - The prevailing unemployment rate
- `"MarkDown1"`, `"MarkDown2"`, `"MarkDown3"`, `"MarkDown4"` - number of promotional markdowns
- `"Dept"` - Department Number in each store
- `"Size"` - size of the store
- `"Type"` - type of the store (depends on `Size` column)

You will need to merge those files and perform some data manipulations. The transformed DataFrame can then be stored as the `clean_data` variable containing the following columns:
- `"Store_ID"`
- `"Month"`
- `"Dept"`
- `"IsHoliday"`
- `"Weekly_Sales"`
- `"CPI"`
- "`"Unemployment"`"
"""

import pandas as pd
import os

# Extract function is already implemented for you
def extract(store_data, extra_data):
    extra_df = pd.read_parquet(extra_data)
    merged_df = store_data.merge(extra_df, on = "index")
    return merged_df

# Call the extract() function and store it as the "merged_df" variable
merged_df = extract(grocery_sales, "extra_data.parquet")

ef transform(raw_data):
    # Data Cleaning
    # Dropping Records w/o Date
    #raw_data.dropna(subset=['Date'], inplace=True)
    # Create Month Column
    raw_data['Month'] = pd.to_datetime(raw_data['Date']).dt.month
    # Fill NA CPI's using records from same date and same store_id.
    raw_data['CPI'] = raw_data.groupby(['Date', 'Store_ID'])['CPI'].apply(lambda x: x.fillna(x.mean()))
    raw_data['Unemployment'].fillna(raw_data['CPI'].mean(), inplace = True)
    # Fill NA Weekly_Sales with 0
    raw_data['Weekly_Sales'].fillna(0, inplace=True)
    # Subset desired columns
    subset = raw_data[['Store_ID', 'Month', 'Dept', 'IsHoliday', 'Weekly_Sales', 'CPI', 'Unemployment']]
    return subset

# Call the transform() function and pass the merged DataFrame
clean_data = transform(merged_df)

# Create the avg_weekly_sales_per_month function that takes in the cleaned data from the last step
def avg_weekly_sales_per_month(clean_data):
    agg = clean_data.groupby('Month')['Weekly_Sales'].sum()
    return agg

agg_data = avg_weekly_sales_per_month(clean_data)

# Create the load() function that takes in the cleaned DataFrame and the aggregated one with the paths where they are going to be stored
def load(full_data, full_data_file_path, agg_data, agg_data_file_path):
    full_data.to_csv(full_data_file_path, index=False)
    agg_data.to_csv(agg_data_file_path, index=False)

# Call the load() function and pass the cleaned and aggregated DataFrames with their paths
load(clean_data, "clean_data.csv", agg_data, "agg_data.csv")

# Create the validation() function with one parameter: file_path - to check whether the previous function was correctly executed
def validation(file_path):
   return os.path.exists(file_path)

validation("clean_data.csv")
validation("agg_data.csv")