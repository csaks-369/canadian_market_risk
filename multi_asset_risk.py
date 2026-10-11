"""
Canadian Market Risk Snapshot
Stocks (XIU), bonds (ZAG) and gold (CGL): volatility, correlation,
portfolios, Value at Risk, stress tests and SQL queries.

Run:  python multi_asset_risk.py
"""
import sqlite3

import numpy as np
import pandas as pd

FILE = "SCENARIO_ANALYSIS_formatted.xlsx"
PORTFOLIO_VALUE = 100_000   # pretend portfolio size in CAD
TRADING_DAYS = 252
Z_95 = 1.645                # 95% confidence, normal distribution

# ---------------------------------------------------------------- 1. LOAD
raw = pd.read_excel(FILE, header=None, skiprows=5, usecols="B,C,G,H,L,M")
prices = pd.DataFrame({
    "Date": raw.iloc[:, 0],
    "Stocks": raw.iloc[:, 1],
    "Bonds": raw.iloc[:, 3],
    "Gold": raw.iloc[:, 5],
}).set_index("Date")

# --------------------------------------------------------------- 2. RETURNS
returns = prices.pct_change().dropna()

# ------------------------------------------------- 3. VOLATILITY, CORRELATION
daily_vol = returns.std()
annual_vol = daily_vol * np.sqrt(TRADING_DAYS)
corr = returns.corr()

# ------------------------------------------------------------ 4. PORTFOLIOS
returns["Equal Weight"] = returns[["Stocks", "Bonds", "Gold"]].mean(axis=1)
returns["Conservative"] = (0.3 * returns["Stocks"]
                           + 0.6 * returns["Bonds"]
                           + 0.1 * returns["Gold"])
port_vol = returns[["Equal Weight", "Conservative"]].std() * np.sqrt(TRADING_DAYS)

# ------------------------------------------------------------- 5. VALUE AT RISK
cols = ["Stocks", "Equal Weight", "Conservative"]
var_param = Z_95 * returns[cols].std() * PORTFOLIO_VALUE
var_hist = -returns[cols].quantile(0.05) * PORTFOLIO_VALUE
worst_day = -returns[cols].min() * PORTFOLIO_VALUE

# ----------------------------------------------------------- 6. STRESS TEST
scenarios = pd.DataFrame({
    "Stocks": [-0.03, -0.15, -0.03, -0.12],
    "Bonds":  [-0.075, 0.02, 0.0, -0.05],
    "Gold":   [-0.02, -0.08, -0.15, -0.10]},
    index=["Rates +1%", "Stock correction", "Gold falls", "Everything falls"])
weights = pd.DataFrame({
    "Stocks only":  [1, 0, 0],
    "Equal Weight": [1/3, 1/3, 1/3],
    "Conservative": [0.3, 0.6, 0.1]},
    index=["Stocks", "Bonds", "Gold"])
stress_pnl = scenarios.dot(weights) * PORTFOLIO_VALUE

# ------------------------------------------------------------------ 7. SQL
conn = sqlite3.connect("risk.db")
db = returns.copy()
db.index = db.index.strftime("%Y-%m-%d")
db.index.name = "date"
db.columns = db.columns.str.replace(" ", "_")
db.to_sql("daily_returns", conn, if_exists="replace")

def q(sql):
    return pd.read_sql(sql, conn)

worst_stock_days = q("SELECT date, ROUND(Stocks*100,2) AS stocks_pct "
                     "FROM daily_returns ORDER BY Stocks LIMIT 5")
all_fell = q("SELECT COUNT(*) AS days_all_fell FROM daily_returns "
             "WHERE Stocks<0 AND Bonds<0 AND Gold<0")
hedge = q("""SELECT COUNT(*) AS total_days, SUM(Stocks<0) AS stock_down,
                    SUM(Stocks<0 AND Bonds<0) AS stock_bond_down,
                    SUM(Stocks<0 AND Bonds>0) AS stock_down_bond_up
             FROM daily_returns""")
monthly = q("""SELECT substr(date,1,7) AS month, COUNT(*) AS days,
                      ROUND(AVG(Stocks)*100,2) AS avg_stocks_pct,
                      ROUND(MIN(Stocks)*100,2) AS worst_day_pct
               FROM daily_returns GROUP BY month ORDER BY month""")
conn.close()

# ------------------------------------------------------------------ REPORT
print("Annual volatility (%)\n", (annual_vol * 100).round(2), "\n")
print("Correlation\n", corr.round(2), "\n")
print("Portfolio annual volatility (%)\n", (port_vol * 100).round(2), "\n")
print("95% VaR, parametric ($)\n", var_param.round(0), "\n")
print("95% VaR, historical ($)\n", var_hist.round(0), "\n")
print("Worst day ($)\n", worst_day.round(0), "\n")
print("Stress test P&L ($)\n", stress_pnl.round(0), "\n")
print("Five worst stock days\n", worst_stock_days, "\n")
print(all_fell, "\n")
print(hedge, "\n")
print(monthly)
