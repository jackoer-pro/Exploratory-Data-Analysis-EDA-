# Retail Intelligence — UCI Online Retail Analysis

## What this project does
Analyses 541,909 transactions from a UK-based wholesale gift retailer 
(Dec 2010 – Dec 2011). Every transaction is classified into 7 types 
— from normal sales to bad debt write-offs — ensuring nothing is 
dropped and every row has a business meaning. The analysis covers 
revenue patterns, customer segmentation using RFM scoring, and product 
quality investigation, producing actionable insights for sales managers 
rather than just charts.

## Key findings
1. **Customer concentration** — 962 Champions (22% of customers) 
   generate 65% of revenue. Losing 10 Champions costs more than 
   losing 100 average customers.

2. **Seasonal peak** — November revenue hits £1.16M, 2× the monthly 
   average. Thursday is peak trading day at £1.97M vs Monday £1.37M.

3. **Product quality crisis** — MEDIUM CERAMIC TOP STORAGE JAR has a 
   95.6% return rate (74,494 of 77,916 units returned). Net revenue 
   on this product is likely negative after return costs.

## Live dashboard
[View live dashboard](https://ffnpx4vhaerhjegvqe4vfg.streamlit.app/)

## Tech stack
- Python, Pandas, Matplotlib, Plotly, Streamlit

## How to run locally
pip install -r requirements.txt
streamlit run app/dashboard.py

## Data source
UCI Machine Learning Repository — Online Retail Dataset
https://archive.ics.uci.edu/dataset/352/online+retail
