-- . Total revenue by country and segment?
SELECT Country,Segment,
SUM(Sales) AS Revenue
FROM financial.`financial sample`
GROUP BY Country,Segment
ORDER BY Revenue DESC;





-- . Profit and Profit margin by country and segment?
SELECT Country,Segment,
SUM(Profit) AS Profit,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY Country,Segment
ORDER BY Profit DESC;





-- . Product with the highest profit margin despite high manufacturing cost?
SELECT Product,
SUM(`Manufacturing Price`) AS Total_manufacturing_price,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY Product
ORDER BY Total_manufacturing_price DESC;





-- .How do discount bands affect both units sold and profit margin?
SELECT `Discount Band`,
SUM(`Units Sold`) AS Total_units_sold,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY `Discount Band`
ORDER BY Total_units_sold DESC;





-- .Months consistently generate the highest and lowest revenue?
SELECT
`Month Name`,`Month Number` ,
SUM(Sales) AS Revenue
FROM financial.`financial sample`
GROUP BY `Month Name` , `Month Number` 
ORDER BY Revenue DESC;






-- .What is the best and least profitable year for the company?
SELECT `Year`,
SUM(Sales) AS Revenue,
SUM(Profit) AS Profit,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY `Year`
ORDER BY Revenue DESC;





-- .Products with the lowest sale price to manufacturing price ratio?
SELECT 
Product,
ROUND(350/AVG(`Manufacturing Price`),2) AS Price_to_Cost_Ratio
FROM financial.`financial sample`
GROUP BY Product
ORDER BY Price_to_Cost_Ratio ASC;





-- .Country and segment combination drives the most profit?
SELECT
Country,Segment,
SUM(Profit) AS Profit 
FROM financial.`financial sample`
GROUP BY Country,Segment
ORDER BY Profit DESC;





-- .Discount rate correlate with profit margin across segments?
SELECT 
Segment,`Discount Band`,
ROUND(SUM(Profit)/SUM(Sales)*100,2) AS Profit_margin
FROM financial.`financial sample`
GROUP BY Segment,`Discount Band`
ORDER BY Profit_margin DESC;





-- .The revenue concentration risk across segments?
SELECT 
Segment,
SUM(Sales) AS Total_Segment_Revenue,
ROUND((SUM(Sales)/SUM(SUM(Sales)) OVER())*100,2) AS Percentage_of_Total_Revenue
FROM financial.`financial sample`
GROUP BY Segment
ORDER BY Percentage_of_Total_Revenue DESC;

















