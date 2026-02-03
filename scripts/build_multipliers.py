import pandas as pd
import json
import os

df = pd.read_csv(r'C:\Users\User\venna-ai\TASI_financials_DB.csv')

# Focus on annual data
annual_df = df[df['is_annual'] == True].copy()
latest_annual = annual_df.sort_values('fiscal_year').groupby('ticker').last().reset_index()

# Known company expected revenues (approximate in billions SAR for 2024/latest)
known_revenues = {
    2222: {'expected_billions': 1600, 'name': 'Saudi Aramco'},          # ~1.6 trillion SAR
    2010: {'expected_billions': 175, 'name': 'SABIC'},                   # ~175 billion
    7010: {'expected_billions': 76, 'name': 'STC'},                      # ~76 billion
    5110: {'expected_billions': 89, 'name': 'Saudi Electricity'},        # ~89 billion
    1180: {'expected_billions': 50, 'name': 'Al Rajhi Bank'},            # ~50 billion (banks use different structure)
    7020: {'expected_billions': 18, 'name': 'Mobily'},                   # ~18 billion
    7030: {'expected_billions': 10, 'name': 'Zain KSA'},                 # ~10 billion
    2280: {'expected_billions': 21, 'name': 'Almarai'},                  # ~21 billion
    2050: {'expected_billions': 24, 'name': 'Savola'},                   # ~24 billion
    1211: {'expected_billions': 33, 'name': 'Ma\'aden'},                 # ~33 billion - appears correct (full SAR)
    4013: {'expected_billions': 11, 'name': 'Dr. Sulaiman Al Habib'},    # ~11 billion
    2380: {'expected_billions': 39, 'name': 'Petro Rabigh'},             # ~39 billion
    4164: {'expected_billions': 9.4, 'name': 'Nahdi Medical'},           # ~9.4 billion - appears correct
    4200: {'expected_billions': 19, 'name': 'Aldrees Petroleum'},        # ~19 billion - appears correct
    4050: {'expected_billions': 10, 'name': 'SASCO'},                    # ~10 billion - appears correct
}

multipliers = {}

print("="*100)
print("UNIT ANALYSIS AND MULTIPLIER DETERMINATION")
print("="*100)

for ticker, info in known_revenues.items():
    company_data = latest_annual[latest_annual['ticker'] == ticker]
    if company_data.empty:
        print(f"\n{ticker} - {info['name']}: NOT FOUND")
        continue

    row = company_data.iloc[0]
    actual_revenue = row['revenue'] if pd.notna(row['revenue']) else 0
    expected_rev_sar = info['expected_billions'] * 1_000_000_000  # Convert to SAR

    if actual_revenue == 0:
        print(f"\n{ticker} - {info['name']}: No revenue data")
        continue

    # Calculate what multiplier would make sense
    if actual_revenue > 0:
        ratio = expected_rev_sar / actual_revenue
    else:
        ratio = 0

    # Determine unit based on ratio
    if 500_000 < ratio < 2_000_000:
        unit = 'millions'
        multiplier = 1_000_000
    elif 500 < ratio < 2_000:
        unit = 'thousands'
        multiplier = 1_000
    else:
        unit = 'SAR'
        multiplier = 1

    print(f"\n{ticker} - {info['name']}:")
    print(f"  Actual value:   {actual_revenue:>20,.0f}")
    print(f"  Expected (SAR): {expected_rev_sar:>20,.0f}")
    print(f"  Ratio:          {ratio:>20,.1f}")
    print(f"  Determined unit: {unit} (multiplier: {multiplier:,})")

    if multiplier != 1:
        multipliers[str(ticker)] = {
            'multiplier': multiplier,
            'unit': unit,
            'company': info['name']
        }

# Now analyze all companies to find others with unit issues
print("\n" + "="*100)
print("ANALYZING ALL COMPANIES FOR UNIT INCONSISTENCIES")
print("="*100)

# Companies reporting in MILLIONS (revenue looks like it should be multiplied by 1,000,000)
# These typically show revenue < 100,000 for major companies
millions_threshold = 100_000  # If revenue is under 100K but company is substantial

# Get companies with very small revenue values that have significant total assets or net profit
for _, row in latest_annual.iterrows():
    ticker = int(row['ticker'])
    if str(ticker) in multipliers:
        continue

    revenue = row['revenue'] if pd.notna(row['revenue']) else 0
    total_assets = row['total_assets'] if pd.notna(row['total_assets']) else 0
    net_profit = row['net_profit'] if pd.notna(row['net_profit']) else 0
    company_name = row['company_name']

    # Skip if no revenue data
    if revenue <= 0:
        continue

    # Pattern 1: Revenue is extremely small (< 50,000) but company has significant assets
    # This indicates MILLIONS unit
    if revenue < 50_000 and total_assets > 1_000_000:
        multipliers[str(ticker)] = {
            'multiplier': 1_000_000,
            'unit': 'millions',
            'company': company_name
        }
        print(f"MILLIONS: {ticker} - {company_name}: Rev={revenue:,.0f}, Assets={total_assets:,.0f}")

    # Pattern 2: Revenue between 50,000 and 1,000,000,000 but seems too small for the company
    # Check if assets/revenue ratio is way off (indicates thousands)
    elif 50_000 <= revenue < 1_000_000_000:
        # If total assets are much larger than expected for SAR revenue, likely thousands
        if total_assets > 0 and total_assets / revenue > 100:
            # This ratio being very high suggests revenue is in thousands
            multipliers[str(ticker)] = {
                'multiplier': 1_000,
                'unit': 'thousands',
                'company': company_name
            }
            print(f"THOUSANDS: {ticker} - {company_name}: Rev={revenue:,.0f}, Assets={total_assets:,.0f}, Ratio={total_assets/revenue:.1f}")

# Insurance companies (8xxx) typically report in thousands
insurance_tickers = [t for t in latest_annual['ticker'].unique() if 8000 <= t < 9000]
for ticker in insurance_tickers:
    if str(ticker) in multipliers:
        continue
    company_data = latest_annual[latest_annual['ticker'] == ticker]
    if company_data.empty:
        continue
    row = company_data.iloc[0]
    revenue = row['revenue'] if pd.notna(row['revenue']) else 0
    company_name = row['company_name']

    # Insurance companies with revenue < 100M SAR but are real companies likely report in thousands
    if 0 < revenue < 100_000_000:
        multipliers[str(ticker)] = {
            'multiplier': 1_000,
            'unit': 'thousands',
            'company': company_name
        }
        print(f"INSURANCE (thousands): {ticker} - {company_name}: Rev={revenue:,.0f}")

# Manual additions based on industry knowledge
manual_additions = {
    # Major companies that need adjustment
    '2222': {'multiplier': 1_000_000, 'unit': 'millions', 'company': 'Saudi Arabian Oil Co.'},
    '2010': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Basic Industries Corp.'},
    '7010': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Telecom Co.'},
    '5110': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Electricity Co.'},
    '7020': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Etihad Etisalat Co.'},
    '7030': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Mobile Telecommunication Company Saudi Arabia'},
    '2280': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Almarai Co.'},
    '2050': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Savola Group'},
    '4013': {'multiplier': 1_000_000, 'unit': 'millions', 'company': 'Dr. Sulaiman Al Habib Medical Services Group'},
    '2380': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Rabigh Refining and Petrochemical Co.'},
    '2290': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Yanbu National Petrochemical Co.'},
    '2310': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Sahara International Petrochemical Co.'},
    '2330': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Advanced Petrochemical Co.'},
    '2060': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'National Industrialization Co.'},
    '2082': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'ACWA POWER Co.'},
    '2083': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'The Power and Water Utility Company for Jubail and Yanbu'},
    '2020': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'SABIC Agri-Nutrients Co.'},
    '4001': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Abdullah Al Othaim Markets Co.'},
    '4003': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'United Electronics Co.'},
    '4030': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'National Shipping Company of Saudi Arabia'},
    '4100': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Makkah Construction and Development Co.'},
    '4190': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Jarir Marketing Co.'},
    '4250': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Jabal Omar Development Co.'},
    '2170': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Alujain Corp.'},
    '2223': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Aramco Base Oil Co.'},
    '2230': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Chemical Co.'},
    '2240': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Zamil Industrial Investment Co.'},
    '4017': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Dr. Soliman Abdel Kader Fakeeh Hospital Co.'},
    '4031': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Ground Services Co.'},
    '4300': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Dar Alarkan Real Estate Development Co.'},
    '4006': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Marketing Co.'},
    '2270': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudia Dairy and Foodstuff Co.'},
    '1302': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Bawan Co.'},
    '1303': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Electrical Industries Co.'},
    '4020': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Real Estate Co.'},
    '4260': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'United International Transportation Co.'},
    '6015': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Americana Restaurants International PLC'},
    '4263': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'SAL Saudi Logistics Services Co.'},
    '3030': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Cement Co.'},
    '2070': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Pharmaceutical Industries and Medical Appliances Corp.'},
    '4040': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Public Transport Co.'},
    '2040': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Ceramic Co.'},
    '2190': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Sustained Infrastructure Holding Co.'},
    '3080': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Eastern Province Cement Co.'},
    '2200': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Arabian Pipes Co.'},
    '2283': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'First Milling Co.'},
    '3040': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Qassim Cement Co.'},
    '3010': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Arabian Cement Co.'},
    '1214': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Al Hassan Ghazi Ibrahim Shaker Co.'},
    '2140': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'AYYAN Investment Co.'},
    '4130': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Darb Investment Co.'},
    '4140': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Saudi Industrial Export Co.'},
    '4170': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Tourism Enterprise Co.'},
    '6020': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Al Gassim Investment Holding Co.'},
    '7202': {'multiplier': 1_000, 'unit': 'thousands', 'company': 'Arabian Internet and Communications Services Co.'},
}

# Add manual additions
for ticker, info in manual_additions.items():
    multipliers[ticker] = info

print("\n" + "="*100)
print(f"TOTAL COMPANIES REQUIRING UNIT CONVERSION: {len(multipliers)}")
print("="*100)

# Save to JSON
output_path = r'C:\Users\User\venna-ai\data\unit_multipliers.json'
with open(output_path, 'w') as f:
    json.dump(multipliers, f, indent=2)

print(f"\nSaved multipliers to: {output_path}")
print("\nSample entries:")
for ticker in list(multipliers.keys())[:10]:
    print(f"  {ticker}: {multipliers[ticker]}")
