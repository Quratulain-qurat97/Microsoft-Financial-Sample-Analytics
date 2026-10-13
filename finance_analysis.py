import pandas as pd

# 1. Load the data
df = pd.read_excel("Financial Sample.csv.xlsx")

# FIX: Remove any accidental leading or trailing spaces from ALL column names
df.columns = df.columns.str.strip()

# 2. Inspect the data
print(df.head())
print(df.info())
print(df.isnull().sum())

# 3. Clean and Transform Data
# Fill missing discount bands with "None"
df["Discount Band"] = df["Discount Band"].fillna("None")


# # 4. Verify the cleanup worked
print("Missing values after cleaning Discount Band:", df["Discount Band"].isnull().sum())
print(df.isnull().sum())

# QUESTION 1: Which country and segment leads in overall revenue?
print("Q1: Sales by Country and Segment")
revenue_by_country_segment = (
    df.groupby(["Country","Segment"])[["Sales"]]
    .sum()
    .reset_index()
    .sort_values(by = "Sales", ascending = False)
)
print(revenue_by_country_segment)


# QUESTION 2: What are the profit and profit margins by country and segment?
print("Q2: Profit and Profit Margin by Country and Segment")

# Step 1: Group by Country & Segment, and sum up both Sales and Profit
country_segment_perf = (
    df.groupby(["Country","Segment"])[["Sales","Profit"]]
    .sum()
    .reset_index()
)
# Step 2: Calculate the Profit Margin on the aggregated totals
country_segment_perf["Profit Margin"] = (
    country_segment_perf["Profit"] / country_segment_perf ["Sales"]
) * 100
# Step 3: Drop 'Sales' by selecting only the columns you actually want to keep
country_segment_perf = country_segment_perf [["Country","Segment","Profit","Profit Margin"]]
# Step 4: Sort by Profit margin in descending order
country_segment_perf = country_segment_perf.sort_values(by = "Profit Margin", ascending = False)
print(country_segment_perf)


# QUESTION 3: Name the Product with the highest profit margin despite high manufacturing cost?
print("Q3: Profit Margin vs. Manufacturing Cost by Product")
product_perf = (
    df.groupby("Product")
    .agg({
       "Sales": "sum",
       "Profit": "sum",
       "Manufacturing Price": "first"
    })
    .reset_index()
)
product_perf["Profit Margin"] = (
    product_perf["Profit"] / product_perf["Sales"] 
) * 100
product_perf = product_perf[["Product", "Manufacturing Price", "Profit", "Profit Margin"]]
product_perf = product_perf.rename(
    columns={"Manufacturing Price": "Manufacturing Price per Unit"}
)
cutoff = product_perf["Manufacturing Price per Unit"].median()
high_cost = product_perf[product_perf["Manufacturing Price per Unit"] > cutoff]
print(high_cost.sort_values("Profit Margin", ascending=False).head(1))

# QUESTION 4: How do discount bands affect both units sold and profit margin?
print("Q4: Discound bands affects on Units Sold and Profit Margin")
# Step 1: Group by Discount, and sum up both Sales, Profit and Units Sold
discount_band_perf = (
    df.groupby("Discount Band")[["Sales","Profit","Units Sold"]]
    .sum()
    .reset_index()
)
# Step 2: Calculate the Profit Margin on the aggregated totals
discount_band_perf ["Profit Margin"] = (
    discount_band_perf["Profit"] / discount_band_perf["Sales"]
) * 100
# Step 3: Drop 'Sales' by selecting only the columns you actually want to keep
discount_band_perf = discount_band_perf [["Discount Band","Units Sold","Profit Margin"]]
# Step 4: Sort by Units Sold in descending order
discount_band_perf = discount_band_perf.sort_values(by = "Units Sold", ascending = False)
print(discount_band_perf)


# QUESTION 5: Which months generate the highest and lowest revenue?
print("Q5: Monthly Revenue")
monthly_revenue = (
    df.groupby(["Month Name","Month Number"])[["Sales"]]
    .sum()
    .reset_index()
    .sort_values(by = "Sales", ascending = False)
)
print(monthly_revenue)


# QUESTION 6: What is the best and least profitable year for the company?
print("Q6: Most Profitable Year")
# Step 1: Group by year, and sum up both Sales and Profit
yearly_profit = (
    df.groupby("Year")[["Sales","Profit"]]
    .sum()
    .reset_index()
)
yearly_profit["Profit Margin"] = (
    yearly_profit["Profit"]/yearly_profit["Sales"]
) * 100
yearly_profit = yearly_profit[["Year","Sales","Profit","Profit Margin"]]
yearly_profit = yearly_profit.sort_values(by = "Profit", ascending = True)
print(yearly_profit)



# QUESTION 7: What are the products with lowest selling-price-to-manufacturing-price ratio?
print("Q7: Products with lowest selling-price-to-manufacturing-price ratio ")
# Step 1: Group by 'Product' and calculate the average prices
product_analysis = (
    df.groupby("Product")
    .agg(
        Avg_Sale_Price = ("Sale Price","mean"),
        Manufacturing_Price = ("Manufacturing Price","first")
    )
    .reset_index()
)
# Step 2: Calculate the price ratio
product_analysis["Price to cost ratio"] =  (
    product_analysis["Avg_Sale_Price"]/product_analysis["Manufacturing_Price"]
).round(2)
# Step 3: Keep only the columns we want to display
product_analysis = product_analysis [["Product","Price to cost ratio"]]
# Step 4: Sort from lowest ratio to highest
product_analysis = product_analysis.sort_values(by = "Price to cost ratio", ascending = True)
print(product_analysis)



# QUESTION 8: Which country and segment combination generates the highest total profit?
print("Q8: Profit by Country and Segment")
# Group by Country & Segment and sum up Profit
profit_by_country_segment = (
    df.groupby(["Country","Segment"])[["Profit"]]
    .sum()
    .reset_index()
)
profit_by_country_segment = profit_by_country_segment.sort_values(by = "Profit", ascending = False)
print(profit_by_country_segment)

result = df.loc[
    (df["Country"] == "France") &
    (df["Segment"] == "Government"),
    "Profit"
].sum()
print(result)


# QUESTION 9: What is the Discount rate correlate with profit margin across segments?
print("Q9: Profit Margin by Segment and Discount Band")
# Step 1: Group by Segment and Discount, and sum up both Sales and Profit
profit_margin_perf = (
    df.groupby(["Segment","Discount Band"])[["Sales","Profit"]]
    .sum()
    .reset_index()
)
# Step 2: Calculate the Profit Margin on the aggregated totals
profit_margin_perf["Profit Margin"] = (
    profit_margin_perf["Profit"]/profit_margin_perf["Sales"]
) * 100

profit_margin_perf = profit_margin_perf.sort_values(by = "Profit Margin", ascending = False)
print(profit_margin_perf[["Segment","Discount Band","Profit Margin"]])



# QUESTION 10: What is the revenue concentration risk across segments?
print("Q10: The revenue concentration risk across segments")
# Step 1. Group by 'Segment' and calculate total revenue for each
segment_revenue = (
    df.groupby("Segment")
    .agg(Total_Revenue=("Sales","sum"))
    .reset_index()
)
# Step 2. Calculate the grand total revenue across all segments
grand_total = segment_revenue["Total_Revenue"].sum()
# Step 3. Calculate the percentage share for each segment and round to 2 decimal places
segment_revenue ["Percentage_of_Total_Revenue"] = round (
    (segment_revenue["Total_Revenue"] / grand_total) * 100,2
)
# Step 4. Sort from highest revenue to lowest
segment_revenue = segment_revenue.sort_values(by = "Percentage_of_Total_Revenue", ascending = False)
print(segment_revenue)


print(df.groupby("Product")["Manufacturing Price"].nunique())
print(df["Product"].value_counts())





print(df[["Sales", "Profit"]].dtypes)

