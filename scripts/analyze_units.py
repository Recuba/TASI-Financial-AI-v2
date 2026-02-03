import pandas as pd
import json
import os

# Read the CSV
df = pd.read_csv(r'C:\Users\User\venna-ai\TASI_financials_DB.csv')

# Focus on annual data for clarity
annual_df = df[df['is_annual'] == True].copy()

# Get unique companies
companies = annual_df[['ticker', 'company_name']].drop_duplicates()
print(f"Total unique companies: {len(companies)}")
print("\n" + "="*80)

# Major companies we know should have large revenues
major_companies = {
    '2222': 'Saudi Aramco',
    '2010': 'SABIC',
    '7010': 'STC',
    '5110': 'Saudi Electricity Co.',
    '1180': 'Al Rajhi Bank',
    '1010': 'Riyad Bank',
    '1120': 'Al Jazira Bank',
    '1140': 'Bank Albilad',
    '1150': 'Alinma Bank',
    '2380': 'Petro Rabigh',
    '2350': 'SABIC Agri-Nutrients',
    '2020': 'Saudi Arabian Mining Co.',
    '4030': 'Bahri',
    '4200': 'Dallah Healthcare',
}

# Get the latest annual data for each company
latest_annual = annual_df.sort_values('fiscal_year').groupby('ticker').last().reset_index()

print("\nAnalyzing major companies (latest annual data):")
print("-" * 80)
for ticker, expected_name in major_companies.items():
    ticker_int = int(ticker)
    company_data = latest_annual[latest_annual['ticker'] == ticker_int]
    if not company_data.empty:
        row = company_data.iloc[0]
        revenue = row['revenue'] if pd.notna(row['revenue']) else 0
        total_assets = row['total_assets'] if pd.notna(row['total_assets']) else 0
        net_profit = row['net_profit'] if pd.notna(row['net_profit']) else 0
        company_name = row['company_name']
        year = row['fiscal_year']
        print(f"\n{ticker} - {company_name} ({year})")
        print(f"  Revenue: {revenue:,.0f}")
        print(f"  Total Assets: {total_assets:,.0f}")
        print(f"  Net Profit: {net_profit:,.0f}")
    else:
        print(f"\n{ticker} - {expected_name}: NOT FOUND")

# Now analyze all companies to detect unit patterns
print("\n" + "="*80)
print("\nAnalyzing all companies to detect unit patterns...")
print("-" * 80)

# Get statistics on revenue values
all_revenues = latest_annual[latest_annual['revenue'].notna()]['revenue']
print(f"\nRevenue statistics across all companies:")
print(f"  Min: {all_revenues.min():,.0f}")
print(f"  Max: {all_revenues.max():,.0f}")
print(f"  Mean: {all_revenues.mean():,.0f}")
print(f"  Median: {all_revenues.median():,.0f}")

# Companies with very small revenue (< 1 billion SAR) - potential millions unit
small_rev = latest_annual[(latest_annual['revenue'].notna()) & (latest_annual['revenue'] < 1_000_000_000)]
print(f"\n\nCompanies with revenue < 1 billion (potential unit issue):")
print("-" * 80)
for _, row in small_rev.sort_values('revenue').iterrows():
    print(f"  {int(row['ticker'])} - {row['company_name']}: {row['revenue']:,.0f}")

# Companies with very large revenue (> 100 billion SAR) - likely full SAR
large_rev = latest_annual[(latest_annual['revenue'].notna()) & (latest_annual['revenue'] > 100_000_000_000)]
print(f"\n\nCompanies with revenue > 100 billion (likely full SAR):")
print("-" * 80)
for _, row in large_rev.sort_values('revenue', ascending=False).iterrows():
    print(f"  {int(row['ticker'])} - {row['company_name']}: {row['revenue']:,.0f}")

# Print all unique tickers with their latest revenue for reference
print("\n" + "="*80)
print("\nAll companies - Latest Annual Revenue (sorted by revenue):")
print("-" * 80)
latest_with_rev = latest_annual[latest_annual['revenue'].notna()].sort_values('revenue')
for _, row in latest_with_rev.iterrows():
    print(f"{int(row['ticker'])},{row['company_name']},{row['revenue']:.0f},{row['fiscal_year']}")
