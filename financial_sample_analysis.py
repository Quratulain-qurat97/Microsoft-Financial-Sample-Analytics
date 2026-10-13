"""
Microsoft Financial Sample - 10-question analysis and audit (pandas)

Purpose
-------
Independent re-verification of the SQL + Power BI project on the Microsoft
Financial Sample dataset (700 rows, 5 segments, 5 countries, 6 products).

How to run
----------
1. Put "Financial Sample.csv.xlsx" in the same folder as this script
   (or change DATA_FILE below).
2. pip install pandas openpyxl
3. python financial_sample_analysis.py

Structure
---------
Part A  Load, clean, reconcile totals against the dashboard / SQL
Part B  Data-quality checks (Manufacturing Price vs COGS, partial year)
Part C  The 10 business questions (Q3 and Q7 are explained in the comments)

Key data notes
--------------
* The Excel file stores the discount band "None" as text; pandas reads it as
  missing, so it is filled back in with "None" (SQL shows the same band).
* 2013 contains only Sep-Dec, 2014 is a full year. Year and month comparisons
  are restricted to like-for-like months.
* The Manufacturing Price column does NOT reconcile with COGS (Part B), so
  cost analysis uses COGS, not Manufacturing Price.
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_FILE = Path("Financial Sample.csv.xlsx")

# Reference totals taken from the Power BI dashboard / SQL
EXPECTED_SALES = 118_726_350.26
EXPECTED_PROFIT = 16_893_702.26

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", "{:,.2f}".format)


def pct(numerator, denominator):
    """Percentage helper used for every margin / share calculation."""
    return numerator / denominator * 100


def check(label, actual, expected, tol=1.0):
    """Print OK / MISMATCH instead of crashing, so the full audit always runs."""
    status = "OK" if abs(actual - expected) <= tol else "MISMATCH"
    print(f"  [{status}] {label}: {actual:,.2f} (expected {expected:,.2f})")


def section(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# PART A - Load, clean, reconcile
# ---------------------------------------------------------------------------
section("PART A: Load, clean and reconcile")

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"'{DATA_FILE}' not found. Place the Excel file next to this script "
        "or update DATA_FILE."
    )

df = pd.read_excel(DATA_FILE)
df.columns = df.columns.str.strip()  # some headers carry leading/trailing spaces

print(df.head().to_string())
df.info()
print(df.isnull().sum())

# Blank Discount Band = the literal "None" band in the source file.
n_blank_band = int(df["Discount Band"].isnull().sum())
df["Discount Band"] = df["Discount Band"].fillna("None")
print(f"\nDiscount Band: filled {n_blank_band} blank cells with 'None' "
      "(matches the 'None' band in the SQL output).")

total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_margin = pct(total_profit, total_sales)

print("\nReconciliation against dashboard / SQL:")
check("Total Sales", total_sales, EXPECTED_SALES)
check("Total Profit", total_profit, EXPECTED_PROFIT)
print(f"  Overall margin: {total_margin:.2f}% (dashboard shows 14.2%)")

print("\nAccounting identities (aggregate):")
check("Gross Sales - Discounts = Sales",
      (df["Gross Sales"] - df["Discounts"]).sum(), total_sales)
check("Sales - COGS = Profit",
      (df["Sales"] - df["COGS"]).sum(), total_profit)

# ---------------------------------------------------------------------------
# PART B - Data-quality checks
# ---------------------------------------------------------------------------
section("PART B: Data-quality checks")

# B1. Manufacturing Price must be constant per product before using "first".
mfg_unique = df.groupby("Product")["Manufacturing Price"].nunique()
print("Distinct Manufacturing Prices per product:")
print(mfg_unique)
assert (mfg_unique == 1).all(), "Manufacturing Price varies within a product"

# B2. Three different "cost" measures - only COGS reconciles with Profit.
print("\nThree cost measures:")
print(f"  Sum of Manufacturing Price column (per-unit price, meaningless): "
      f"{df['Manufacturing Price'].sum():,.0f}")
print(f"  Manufacturing Price x Units Sold:                                "
      f"{(df['Manufacturing Price'] * df['Units Sold']).sum():,.0f}")
print(f"  COGS (reconciles with Profit):                                   "
      f"{df['COGS'].sum():,.0f}")

# B3. Does COGS actually follow Manufacturing Price?
df["Implied Unit COGS"] = df["COGS"] / df["Units Sold"].replace(0, np.nan)
print("\nImplied unit COGS (COGS / Units Sold) vs Manufacturing Price, by product:")
print(df.groupby("Product")[["Manufacturing Price", "Implied Unit COGS"]]
      .agg(["min", "max"]))
print("-> If implied unit COGS ranges widely for every product, "
      "Manufacturing Price is not what drives COGS.")

# B4. Rows that sell below 'Manufacturing Price' yet show a profit.
odd = df[(df["Sale Price"] < df["Manufacturing Price"]) & (df["Profit"] > 0)]
print(f"\nRows with Sale Price < Manufacturing Price but Profit > 0: "
      f"{len(odd)} of {len(df)}")
print(odd["Product"].value_counts().to_dict())

# B5. Partial year.
months_per_year = df.groupby("Year")["Month Number"].nunique()
print("\nMonths of data per year:")
print(months_per_year)
first_year, last_year = df["Year"].min(), df["Year"].max()
overlap_months = sorted(int(m) for m in df.loc[df["Year"] == first_year, "Month Number"].unique())
print(f"{first_year} months present: {overlap_months} "
      f"-> like-for-like comparisons use these months only.")

# ---------------------------------------------------------------------------
# PART C - The 10 questions
# ---------------------------------------------------------------------------
section("PART C: Business questions")

# Q1 ------------------------------------------------------------------------
print("\nQ1: Which country and segment lead in revenue?")
q1 = (df.groupby(["Country", "Segment"])[["Sales"]].sum()
        .reset_index().sort_values("Sales", ascending=False))
print(q1)

# Q2 ------------------------------------------------------------------------
# Margin alone is misleading (Channel Partners: ~73% margin on ~1.5% of
# revenue), so revenue and revenue share are shown next to it.
print("\nQ2: Profit and margin by country and segment (with revenue scale)")
q2 = df.groupby(["Country", "Segment"])[["Sales", "Profit"]].sum().reset_index()
q2["Profit Margin %"] = pct(q2["Profit"], q2["Sales"])
q2["Revenue Share %"] = pct(q2["Sales"], q2["Sales"].sum())
print(q2.sort_values("Profit Margin %", ascending=False))

# Q3 ------------------------------------------------------------------------
# The original question ("highest margin despite high manufacturing cost")
# assumed Manufacturing Price drives cost. Part B shows it does not, so this
# answers the supportable version: COGS and margin by product.
print("\nQ3: COGS and profit margin by product (COGS-based; see Part B)")
q3 = df.groupby("Product")[["Sales", "COGS", "Profit"]].sum().reset_index()
q3["Profit Margin %"] = pct(q3["Profit"], q3["Sales"])
print(q3.sort_values("Profit Margin %", ascending=False))
margin_spread = q3["Profit Margin %"].max() - q3["Profit Margin %"].min()
print(f"Margin spread across products: {margin_spread:.2f} percentage points")

# Q4 ------------------------------------------------------------------------
# Sales is net of discount while costs are fixed, so margin falls with deeper
# discounts partly by construction. Segment mix also differs across bands.
print("\nQ4: Discount band vs units sold and profit margin")
q4 = df.groupby("Discount Band")[["Sales", "Profit", "Units Sold"]].sum().reset_index()
q4["Profit Margin %"] = pct(q4["Profit"], q4["Sales"])
print(q4[["Discount Band", "Units Sold", "Profit Margin %"]]
      .sort_values("Units Sold", ascending=False))

# Q5 ------------------------------------------------------------------------
# Pooling both years double-counts Sep-Dec, so months are shown per year and
# compared like-for-like.
print("\nQ5: Monthly revenue by year")
q5 = (df.groupby(["Year", "Month Number", "Month Name"])["Sales"].sum()
        .reset_index())
print(q5)

print(f"\nQ5b: Like-for-like months only ({overlap_months}), "
      f"{first_year} vs {last_year}")
lfl = (df[df["Month Number"].isin(overlap_months)]
       .pivot_table(index=["Month Number", "Month Name"], columns="Year",
                    values="Sales", aggfunc="sum"))
lfl["YoY %"] = (lfl[last_year] / lfl[first_year] - 1) * 100
print(lfl)
lfl_totals = lfl[[first_year, last_year]].sum()
print(f"Like-for-like total: {first_year} {lfl_totals[first_year]:,.0f} -> "
      f"{last_year} {lfl_totals[last_year]:,.0f} "
      f"({(lfl_totals[last_year] / lfl_totals[first_year] - 1) * 100:+.1f}%)")

# Q6 ------------------------------------------------------------------------
print("\nQ6: Profit by year (note months covered - first year is partial)")
q6 = (df.groupby("Year")
        .agg(Months=("Month Number", "nunique"), Sales=("Sales", "sum"),
             Profit=("Profit", "sum"))
        .reset_index())
q6["Profit Margin %"] = pct(q6["Profit"], q6["Sales"])
print(q6.sort_values("Profit", ascending=False))

print("\nQ6b: Like-for-like months only")
q6b = (df[df["Month Number"].isin(overlap_months)]
       .groupby("Year")[["Sales", "Profit"]].sum().reset_index())
q6b["Profit Margin %"] = pct(q6b["Profit"], q6b["Sales"])
print(q6b)

# Q7 ------------------------------------------------------------------------
# DATA-QUALITY CHECK ONLY - not a business finding. Sale Price is below
# Manufacturing Price for some products yet they are profitable, because COGS
# does not follow the Manufacturing Price column (Part B).
print("\nQ7 (data-quality only): average Sale Price / Manufacturing Price column")
q7 = (df.groupby("Product")
        .agg(Avg_Sale_Price=("Sale Price", "mean"),
             Manufacturing_Price=("Manufacturing Price", "first"))
        .reset_index())
q7["Price to Cost Ratio"] = (q7["Avg_Sale_Price"] / q7["Manufacturing_Price"]).round(2)
print(q7[["Product", "Price to Cost Ratio"]].sort_values("Price to Cost Ratio"))
print("-> Do NOT read ratios < 1 as 'sold below cost'; these products are profitable.")

# Q8 ------------------------------------------------------------------------
print("\nQ8: Profit by country and segment")
q8 = (df.groupby(["Country", "Segment"])[["Profit"]].sum()
        .reset_index().sort_values("Profit", ascending=False))
print(q8)
top = q8.iloc[0]
print(f"Top pair: {top['Country']} / {top['Segment']} ({top['Profit']:,.2f})")

# Q9 ------------------------------------------------------------------------
print("\nQ9: Profit margin by segment and discount band")
q9 = df.groupby(["Segment", "Discount Band"])[["Sales", "Profit"]].sum().reset_index()
q9["Profit Margin %"] = pct(q9["Profit"], q9["Sales"])
print(q9.sort_values("Profit Margin %", ascending=False)
        [["Segment", "Discount Band", "Profit Margin %"]])

# Discount rate = Discounts / Gross Sales (same definition as the dashboard KPI).
seg_rate = df.groupby("Segment")[["Discounts", "Gross Sales"]].sum()
seg_rate["Discount Rate % (of gross)"] = pct(seg_rate["Discounts"], seg_rate["Gross Sales"])
print("\nQ9b: Discount rate by segment (Discounts / Gross Sales)")
print(seg_rate[["Discount Rate % (of gross)"]])
print(f"Overall discount rate: "
      f"{pct(df['Discounts'].sum(), df['Gross Sales'].sum()):.2f}%")

print("\nQ9 conclusion:")
print("  - Within every segment, margin falls at each step up in discount band. "
      "COGS does not change with the discount while Sales is net of it, so this "
      "is largely arithmetic, not a behavioural finding.")
print("  - Across segments, discount rates are similar (about 6.9% to 7.8%) but "
      "margins range from -3% to 73%, so discount rate alone does not explain "
      "the segment gaps.")

# Q10 -----------------------------------------------------------------------
print("\nQ10: Revenue concentration by segment")
q10 = df.groupby("Segment").agg(Total_Revenue=("Sales", "sum")).reset_index()
q10["Percentage_of_Total_Revenue"] = pct(q10["Total_Revenue"],
                                         q10["Total_Revenue"].sum()).round(2)
print(q10.sort_values("Percentage_of_Total_Revenue", ascending=False))

section("END OF ANALYSIS")