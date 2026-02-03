"""
Validation script to verify the normalized TASI financial data.
"""

import pandas as pd

# Load normalized data
df = pd.read_csv(r'C:\Users\User\venna-ai\data\TASI_financials_normalized.csv')

# Get latest annual data
annual_df = df[df['is_annual'] == True]
latest = annual_df.sort_values('fiscal_year').groupby('ticker').last().reset_index()

print("="*100)
print("TOP 25 COMPANIES BY REVENUE (NORMALIZED TO FULL SAR)")
print("="*100)

# Sort by revenue
top_by_revenue = latest[latest['revenue'].notna()].sort_values('revenue', ascending=False).head(25)

print(f"\n{'Ticker':<8} {'Company':<50} {'Revenue (B SAR)':<18} {'Net Profit (B)':<15} {'Unit':<10}")
print("-"*100)

for _, row in top_by_revenue.iterrows():
    ticker = int(row['ticker'])
    company = row['company_name'][:48]
    revenue_b = row['revenue'] / 1_000_000_000 if pd.notna(row['revenue']) else 0
    net_profit_b = row['net_profit'] / 1_000_000_000 if pd.notna(row['net_profit']) else 0
    unit = row['original_unit']
    print(f"{ticker:<8} {company:<50} {revenue_b:>15,.2f} B  {net_profit_b:>12,.2f} B  {unit:<10}")

print("\n" + "="*100)
print("VALIDATION CHECKS")
print("="*100)

# Check Saudi Aramco
aramco = latest[latest['ticker'] == 2222]
if not aramco.empty:
    aramco_rev = aramco['revenue'].values[0] / 1_000_000_000_000
    print(f"\nSaudi Aramco (2222) Revenue: {aramco_rev:.2f} TRILLION SAR")
    if 1.5 < aramco_rev < 2.0:
        print("  [PASS] Revenue is in expected range (1.5-2.0 trillion SAR)")
    else:
        print("  [WARNING] Revenue outside expected range")

# Check SABIC
sabic = latest[latest['ticker'] == 2010]
if not sabic.empty:
    sabic_rev = sabic['revenue'].values[0] / 1_000_000_000
    print(f"\nSABIC (2010) Revenue: {sabic_rev:.2f} BILLION SAR")
    if 150 < sabic_rev < 200:
        print("  [PASS] Revenue is in expected range (150-200 billion SAR)")
    else:
        print("  [WARNING] Revenue outside expected range")

# Check STC
stc = latest[latest['ticker'] == 7010]
if not stc.empty:
    stc_rev = stc['revenue'].values[0] / 1_000_000_000
    print(f"\nSTC (7010) Revenue: {stc_rev:.2f} BILLION SAR")
    if 70 < stc_rev < 90:
        print("  [PASS] Revenue is in expected range (70-90 billion SAR)")
    else:
        print("  [WARNING] Revenue outside expected range")

# Check Dr. Sulaiman Al Habib
dsh = latest[latest['ticker'] == 4013]
if not dsh.empty:
    dsh_rev = dsh['revenue'].values[0] / 1_000_000_000
    print(f"\nDr. Sulaiman Al Habib (4013) Revenue: {dsh_rev:.2f} BILLION SAR")
    if 10 < dsh_rev < 15:
        print("  [PASS] Revenue is in expected range (10-15 billion SAR)")
    else:
        print("  [WARNING] Revenue outside expected range")

# Distribution of original units
print("\n" + "="*100)
print("DATA DISTRIBUTION BY ORIGINAL UNIT")
print("="*100)
unit_counts = df.groupby('original_unit').size()
print(unit_counts)

# Total market statistics
print("\n" + "="*100)
print("MARKET STATISTICS (Latest Annual Data)")
print("="*100)
total_revenue = latest['revenue'].sum() / 1_000_000_000_000
total_assets = latest['total_assets'].sum() / 1_000_000_000_000
total_profit = latest['net_profit'].sum() / 1_000_000_000_000
print(f"Total Market Revenue: {total_revenue:.2f} TRILLION SAR")
print(f"Total Market Assets:  {total_assets:.2f} TRILLION SAR")
print(f"Total Market Profit:  {total_profit:.2f} TRILLION SAR")
