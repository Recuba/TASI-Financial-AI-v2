"""
TASI Financial Data Unit Normalization Script
=============================================
This script normalizes all monetary values in the TASI financials database
to full SAR (Saudi Riyal) values.

Companies report in different units:
- Some in full SAR
- Some in thousands SAR (need to multiply by 1,000)
- Some in millions SAR (need to multiply by 1,000,000)

This script reads the multiplier mapping and applies corrections.
"""

import pandas as pd
import json
import os
from datetime import datetime

# File paths
INPUT_CSV = r'C:\Users\User\venna-ai\TASI_financials_DB.csv'
MULTIPLIERS_JSON = r'C:\Users\User\venna-ai\data\unit_multipliers.json'
OUTPUT_CSV = r'C:\Users\User\venna-ai\data\TASI_financials_normalized.csv'

# Monetary columns that need unit conversion
MONETARY_COLUMNS = [
    'revenue',
    'cost_of_sales',
    'gross_profit',
    'operating_profit',
    'net_profit',
    'interest_expense',
    'total_assets',
    'total_equity',
    'total_liabilities',
    'current_assets',
    'current_liabilities',
    'inventory',
    'receivables',
    'operating_cash_flow',
    'capex',
    'free_cash_flow',
    'working_capital',
    'gross_profit_calc',
    'total_liabilities_calc',
    'free_cash_flow_calc',
    'working_capital_calc',
    'capex_adjusted',
]

# Columns that are already normalized or derived (in millions) - also need conversion
MILLIONS_COLUMNS = [
    'revenue_millions',
    'net_profit_millions',
    'total_assets_millions',
    'total_equity_millions',
]

def load_multipliers():
    """Load the unit multiplier mapping from JSON file."""
    with open(MULTIPLIERS_JSON, 'r') as f:
        multipliers = json.load(f)
    print(f"Loaded multipliers for {len(multipliers)} companies")
    return multipliers

def normalize_data(df, multipliers):
    """Apply unit multipliers to normalize all monetary values to full SAR."""

    # Create a copy to avoid modifying original
    df_normalized = df.copy()

    # Track statistics
    rows_modified = 0
    companies_modified = set()

    # Process each row
    for idx, row in df_normalized.iterrows():
        ticker = str(int(row['ticker'])) if pd.notna(row['ticker']) else None

        if ticker and ticker in multipliers:
            multiplier = multipliers[ticker]['multiplier']
            companies_modified.add(ticker)
            rows_modified += 1

            # Apply multiplier to all monetary columns
            for col in MONETARY_COLUMNS:
                if col in df_normalized.columns:
                    val = row[col]
                    if pd.notna(val) and val != 0:
                        df_normalized.at[idx, col] = val * multiplier

            # Handle the "_millions" columns specially - they need different treatment
            # These are already supposed to be in millions, but based on wrong base values
            # So we multiply by the same factor
            for col in MILLIONS_COLUMNS:
                if col in df_normalized.columns:
                    val = row[col]
                    if pd.notna(val) and val != 0:
                        df_normalized.at[idx, col] = val * multiplier

    print(f"\nNormalization Statistics:")
    print(f"  Total rows processed: {len(df_normalized)}")
    print(f"  Rows modified: {rows_modified}")
    print(f"  Companies with unit corrections: {len(companies_modified)}")

    return df_normalized, companies_modified

def add_normalization_metadata(df, multipliers):
    """Add columns to indicate original unit and if data was normalized."""
    df['original_unit'] = 'SAR'
    df['was_normalized'] = False
    df['normalization_multiplier'] = 1

    for idx, row in df.iterrows():
        ticker = str(int(row['ticker'])) if pd.notna(row['ticker']) else None
        if ticker and ticker in multipliers:
            df.at[idx, 'original_unit'] = multipliers[ticker]['unit']
            df.at[idx, 'was_normalized'] = True
            df.at[idx, 'normalization_multiplier'] = multipliers[ticker]['multiplier']

    return df

def validate_normalization(df_original, df_normalized, multipliers):
    """Validate the normalization by checking key companies."""

    print("\n" + "="*80)
    print("VALIDATION: Comparing Before and After for Key Companies")
    print("="*80)

    # Focus on annual data for clarity
    annual_orig = df_original[df_original['is_annual'] == True]
    annual_norm = df_normalized[df_normalized['is_annual'] == True]

    # Get latest annual for each company
    latest_orig = annual_orig.sort_values('fiscal_year').groupby('ticker').last().reset_index()
    latest_norm = annual_norm.sort_values('fiscal_year').groupby('ticker').last().reset_index()

    key_companies = [2222, 2010, 7010, 5110, 2280, 2050, 4013, 1211, 4164, 4200]

    for ticker in key_companies:
        orig_data = latest_orig[latest_orig['ticker'] == ticker]
        norm_data = latest_norm[latest_norm['ticker'] == ticker]

        if orig_data.empty or norm_data.empty:
            continue

        orig_rev = orig_data['revenue'].values[0] if pd.notna(orig_data['revenue'].values[0]) else 0
        norm_rev = norm_data['revenue'].values[0] if pd.notna(norm_data['revenue'].values[0]) else 0
        company_name = orig_data['company_name'].values[0]

        ticker_str = str(ticker)
        if ticker_str in multipliers:
            mult = multipliers[ticker_str]['multiplier']
            unit = multipliers[ticker_str]['unit']
        else:
            mult = 1
            unit = 'SAR'

        print(f"\n{ticker} - {company_name}")
        print(f"  Original revenue:   {orig_rev:>25,.0f} ({unit})")
        print(f"  Normalized revenue: {norm_rev:>25,.0f} SAR")
        print(f"  Multiplier applied: {mult:>25,}")

        # Convert to billions for readability
        norm_billions = norm_rev / 1_000_000_000
        print(f"  In billions SAR:    {norm_billions:>25,.2f} B")

def main():
    """Main function to run the normalization process."""

    print("="*80)
    print("TASI Financial Data Unit Normalization")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    # Load data
    print(f"\nLoading data from: {INPUT_CSV}")
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    print(f"Unique companies: {df['ticker'].nunique()}")

    # Load multipliers
    print(f"\nLoading multipliers from: {MULTIPLIERS_JSON}")
    multipliers = load_multipliers()

    # Normalize data
    print("\nApplying unit normalization...")
    df_normalized, companies_modified = normalize_data(df, multipliers)

    # Add metadata columns
    print("\nAdding normalization metadata columns...")
    df_normalized = add_normalization_metadata(df_normalized, multipliers)

    # Validate
    validate_normalization(df, df_normalized, multipliers)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # Save normalized data
    print(f"\nSaving normalized data to: {OUTPUT_CSV}")
    df_normalized.to_csv(OUTPUT_CSV, index=False)

    # Calculate file sizes
    input_size = os.path.getsize(INPUT_CSV) / (1024 * 1024)
    output_size = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)

    print(f"\nFile sizes:")
    print(f"  Input:  {input_size:.2f} MB")
    print(f"  Output: {output_size:.2f} MB")

    print("\n" + "="*80)
    print("NORMALIZATION COMPLETE")
    print("="*80)

    # Print summary of what was modified
    print(f"\nCompanies with unit corrections ({len(companies_modified)} total):")

    # Group by multiplier type
    millions = [t for t in companies_modified if multipliers.get(t, {}).get('multiplier') == 1000000]
    thousands = [t for t in companies_modified if multipliers.get(t, {}).get('multiplier') == 1000]

    print(f"\n  Converted from MILLIONS SAR ({len(millions)} companies):")
    for t in sorted(millions)[:10]:
        print(f"    - {t}: {multipliers[t]['company']}")
    if len(millions) > 10:
        print(f"    ... and {len(millions) - 10} more")

    print(f"\n  Converted from THOUSANDS SAR ({len(thousands)} companies):")
    for t in sorted(thousands)[:10]:
        print(f"    - {t}: {multipliers[t]['company']}")
    if len(thousands) > 10:
        print(f"    ... and {len(thousands) - 10} more")

    return df_normalized

if __name__ == '__main__':
    main()
