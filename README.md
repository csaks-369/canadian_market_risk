# Canadian Market Risk Snapshot

How risky is it to hold Canadian stocks, bonds and gold? This project measures volatility, correlation, Value at Risk (VaR) and stress-test losses for three Canadian ETFs and two portfolios, using Excel, Python and SQL.

**Data:** one year of daily closing prices (6 Oct 2025 to 2 Oct 2026) from Google Finance.

| Asset | ETF |
|---|---|
| Stocks | XIU (S&P/TSX 60) |
| Bonds | ZAG (Canadian aggregate bonds) |
| Gold | CGL (gold bullion) |

**Portfolios compared:** Equal Weight (one third each) and Conservative (30% stocks, 60% bonds, 10% gold).

## Key findings

| Asset | Annual volatility |
|---|---|
| Bonds | 4.74% |
| Stocks | 12.46% |
| Gold | 30.08% |

- Correlations are all positive (stocks-bonds 0.41, stocks-gold 0.56, bonds-gold 0.19), so diversification helps only partly. On the 102 days stocks fell, bonds rose on only 36.
- Equal Weight (13.37% volatility) is riskier than stocks alone (12.46%), because of gold. Conservative is the lowest at 7.46%.
- 95% daily VaR per $100,000 (parametric / historical): Stocks $1,292 / $1,342, Equal Weight $1,385 / $1,382, Conservative $774 / $756.
- In the stress test, Conservative loses the most when rates rise 1% (-$5,600), because 60% of it is in bonds. It loses the least in a stock correction or a gold decline. Low volatility does not mean safe in every scenario.

Stress-test shocks are assumptions, not forecasts (for example, a bond duration of about 7.5 years for ZAG).

## What the script does

1. Loads closing prices from the Excel file.
2. Calculates daily returns, annualized volatility (daily volatility x sqrt(252)) and correlations.
3. Builds the two portfolios and measures their volatility.
4. Calculates 95% VaR two ways: parametric (1.645 x daily volatility) and historical (5th percentile).
5. Applies four stress scenarios: rates +1%, stock correction, gold falls, everything falls.
6. Saves returns to a SQLite database and answers risk questions with SQL (worst days, days all assets fell, hedge behaviour, monthly summary).

## How to run

```
pip install -r requirements.txt
python multi_asset_risk.py
```

Keep `SCENARIO_ANALYSIS_formatted.xlsx` in the same folder as the script. The script creates `risk.db` when it runs.

## Files

| File | Purpose |
|---|---|
| `multi_asset_risk.py` | Full analysis in Python and SQL |
| `multi_asset_risk_py.ipynb` | Step-by-step notebook with saved outputs |
| `SCENARIO_ANALYSIS_formatted.xlsx` | Excel version: prices, returns, volatility, correlation, portfolios |
| `requirements.txt` | Python packages needed |

## Limitations

- One year of data and prices only (no dividends or interest).
- VaR assumes the recent past represents the future and understates extreme days.
- Stress-test shocks are chosen assumptions.
- Currency hedging of the gold ETF was not checked.

## Possible next steps

Monte Carlo VaR, a GARCH volatility model for clustering of bad days, and a longer history that includes 2020 and 2022.

*Author: Arshleen Kaur Saluja*
