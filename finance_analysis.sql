-- Microsoft Financial Sample: 10-question analysis (MySQL 8+, uses a window function in Q10)
-- Table: financial.`financial sample` (700 rows, single flat table)
-- 2013 covers Sep-Dec only, so Q5b and Q6b compare like-for-like months.
-- Totals may differ from the pandas script by a few dollars because of rounding on import.


-- Q1. Total revenue by country and segment?
SELECT Country,Segment,
SUM(Sales) AS Revenue
FROM financial.`financial sample`
GROUP BY Country,Segment
ORDER BY Revenue DESC;





-- Q2. Profit and Profit margin by country and segment?
SELECT Country,Segment,
SUM(Profit) AS Profit,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY Country,Segment
ORDER BY Profit DESC;





-- Q3. Profit margin and COGS by product
-- Note: Manufacturing Price does not reconcile with COGS in this dataset, 
-- so cost is measured with COGS.
SELECT Product,
SUM(Sales) AS Revenue,SUM(COGS) AS Total_COGS,SUM(Profit) AS Profit,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY Product
ORDER BY Profit_margin DESC;





-- Q4.How do discount bands affect both units sold and profit margin?
SELECT `Discount Band`,
SUM(`Units Sold`) AS Total_units_sold,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY `Discount Band`
ORDER BY Total_units_sold DESC;





-- Q5. Monthly revenue by year (2013 covers Sep-Dec only)
SELECT `Year`, `Month Number`, `Month Name`,SUM(Sales) AS Revenue
FROM financial.`financial sample`
GROUP BY `Year`, `Month Number`, `Month Name`
ORDER BY `Year`, `Month Number`;

-- Q5b. Like-for-like months only (Sep-Dec), 2013 vs 2014
SELECT `Month Number`, `Month Name`,
SUM(CASE WHEN `Year` = 2013 THEN Sales END) AS Revenue_2013,
SUM(CASE WHEN `Year` = 2014 THEN Sales END) AS Revenue_2014,
ROUND((SUM(CASE WHEN `Year` = 2014 THEN Sales END)/ SUM(CASE WHEN `Year` = 2013 THEN Sales END) - 1) * 100, 2) AS YoY_pct
FROM financial.`financial sample`
WHERE `Month Number` IN (9, 10, 11, 12)
GROUP BY `Month Number`, `Month Name`
ORDER BY `Month Number`;






-- Q6. Profit by year (2013 is a partial year: Sep-Dec only)
SELECT `Year`,COUNT(DISTINCT `Month Number`) AS Months_Covered,SUM(Sales) AS Revenue,
SUM(Profit) AS Profit,ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY `Year`
ORDER BY Profit DESC;

-- Q6b. Like-for-like months only
SELECT `Year`,SUM(Sales) AS Revenue,SUM(Profit) AS Profit,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
WHERE `Month Number` IN (9, 10, 11, 12)
GROUP BY `Year`
ORDER BY `Year`;




-- Q7. Data-quality check only (not a finding): avg Sale Price / Manufacturing Price column.
-- Ratios below 1 do not mean products sell below cost; Manufacturing Price does not reconcile 
-- with COGS.
SELECT 
Product,
ROUND(AVG(`Sale Price`)/AVG(`Manufacturing Price`),2) AS Price_to_Cost_Ratio
FROM financial.`financial sample`
GROUP BY Product
ORDER BY Price_to_Cost_Ratio ASC;





-- Q8.Country and segment combination drives the most profit?
SELECT
Country,Segment,
SUM(Profit) AS Profit 
FROM financial.`financial sample`
GROUP BY Country,Segment
ORDER BY Profit DESC;




-- Q9. Profit margin by segment and discount band
SELECT 
Segment,`Discount Band`,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY Segment,`Discount Band`
ORDER BY Profit_margin DESC;

-- Q9b. Discount rate by segment (Discounts / Gross Sales, same definition as the dashboard)
SELECT Segment,
ROUND(SUM(Discounts)/SUM(`Gross Sales`)*100,2) AS Discount_rate_pct
FROM financial.`financial sample`
GROUP BY Segment
ORDER BY Discount_rate_pct DESC;




-- Q10.The revenue concentration risk across segments?
SELECT 
Segment,
SUM(Sales) AS Total_Segment_Revenue,
ROUND((SUM(Sales)/SUM(SUM(Sales)) OVER())*100,2) AS Percentage_of_Total_Revenue
FROM financial.`financial sample`
GROUP BY Segment
ORDER BY Percentage_of_Total_Revenue DESC;

















