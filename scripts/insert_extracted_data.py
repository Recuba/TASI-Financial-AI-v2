#!/usr/bin/env python3
"""
TASI Financial Database Insertion Script
Author: Database Engineer
Date: 2026-02-03

This script inserts validated financial records from INSERT_READY.csv
into the TASI_financials_DB.csv database.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# File paths
INSERT_READY_PATH = r"C:\Users\User\venna-ai\data\extracted\INSERT_READY.csv"
DB_PATH = r"C:\Users\User\venna-ai\TASI_financials_DB.csv"
LOG_PATH = r"C:\Users\User\venna-ai\data\insertion_log_20260203.txt"

# Initialize log
log_messages = []

def log(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    log_messages.append(log_message)

def calculate_derived_fields(df):
    """Calculate derived financial metrics for records"""
    log("Calculating derived financial metrics...")

    # Make a copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Financial ratios
    df['calc_ROE'] = np.where(
        (df['total_equity'] != 0) & (df['net_profit'].notna()),
        (df['net_profit'] / df['total_equity']) * 100,
        np.nan
    )

    df['calc_ROA'] = np.where(
        (df['total_assets'] != 0) & (df['net_profit'].notna()),
        (df['net_profit'] / df['total_assets']) * 100,
        np.nan
    )

    df['calc_gross_margin'] = np.where(
        (df['revenue'] != 0) & (df['gross_profit'].notna()),
        (df['gross_profit'] / df['revenue']) * 100,
        np.nan
    )

    df['calc_operating_margin'] = np.where(
        (df['revenue'] != 0) & (df['operating_profit'].notna()),
        (df['operating_profit'] / df['revenue']) * 100,
        np.nan
    )

    df['calc_net_margin'] = np.where(
        (df['revenue'] != 0) & (df['net_profit'].notna()),
        (df['net_profit'] / df['revenue']) * 100,
        np.nan
    )

    df['calc_current_ratio'] = np.where(
        (df['current_liabilities'] != 0) & (df['current_assets'].notna()),
        df['current_assets'] / df['current_liabilities'],
        np.nan
    )

    df['calc_quick_ratio'] = np.where(
        (df['current_liabilities'] != 0) & (df['current_assets'].notna()) & (df['inventory'].notna()),
        (df['current_assets'] - df['inventory']) / df['current_liabilities'],
        np.nan
    )

    df['calc_debt_to_equity'] = np.where(
        (df['total_equity'] != 0) & (df['total_liabilities'].notna()),
        (df['total_liabilities'] / df['total_equity']) * 100,
        np.nan
    )

    df['calc_debt_to_assets'] = np.where(
        (df['total_assets'] != 0) & (df['total_liabilities'].notna()),
        (df['total_liabilities'] / df['total_assets']) * 100,
        np.nan
    )

    df['calc_asset_turnover'] = np.where(
        (df['total_assets'] != 0) & (df['revenue'].notna()),
        df['revenue'] / df['total_assets'],
        np.nan
    )

    df['calc_working_capital'] = np.where(
        (df['current_assets'].notna()) & (df['current_liabilities'].notna()),
        df['current_assets'] - df['current_liabilities'],
        np.nan
    )

    # Metadata fields
    df['period_label'] = df['period_type'].apply(lambda x: f"FY{df.loc[df['period_type'] == x, 'fiscal_year'].iloc[0]}" if x == 'Annual' else 'Q')
    df['revenue_millions'] = df['revenue'] / 1_000_000
    df['net_profit_millions'] = df['net_profit'] / 1_000_000
    df['total_assets_millions'] = df['total_assets'] / 1_000_000
    df['total_equity_millions'] = df['total_equity'] / 1_000_000

    df['roe_pct'] = df['calc_ROE']
    df['roa_pct'] = df['calc_ROA']
    df['gross_margin_pct'] = df['calc_gross_margin']
    df['operating_margin_pct'] = df['calc_operating_margin']
    df['net_margin_pct'] = df['calc_net_margin']
    df['debt_to_equity_pct'] = df['calc_debt_to_equity']
    df['debt_to_assets_pct'] = df['calc_debt_to_assets']

    df['is_annual'] = df['period_type'] == 'Annual'
    df['is_latest'] = False  # Will be updated later

    df['period_date'] = pd.to_datetime(df['period_end'], errors='coerce')
    df['year_quarter'] = df.apply(
        lambda row: f"{row['fiscal_year']}-FY" if row['period_type'] == 'Annual' else f"{row['fiscal_year']}-Q{pd.to_datetime(row['period_end']).quarter}",
        axis=1
    )

    # Status fields
    df['profit_status'] = np.where(df['net_profit'] > 0, 'Profit',
                                    np.where(df['net_profit'] < 0, 'Loss', 'N/A'))

    df['has_cogs'] = df['cost_of_sales'].notna()
    df['has_operating_profit'] = df['operating_profit'].notna()

    df['ticker_name'] = df['ticker'].astype(str) + ' - ' + df['company_name']

    # Decimal versions of percentages
    df['roe_decimal'] = df['calc_ROE'] / 100
    df['roa_decimal'] = df['calc_ROA'] / 100
    df['gross_margin_decimal'] = df['calc_gross_margin'] / 100
    df['operating_margin_decimal'] = df['calc_operating_margin'] / 100
    df['net_margin_decimal'] = df['calc_net_margin'] / 100

    return df

def main():
    log("="*80)
    log("TASI Financial Database Insertion Script")
    log("="*80)

    # Load INSERT_READY data
    log(f"Loading validated records from: {INSERT_READY_PATH}")
    try:
        new_data = pd.read_csv(INSERT_READY_PATH)
        log(f"Successfully loaded {len(new_data)} records from INSERT_READY.csv")
    except Exception as e:
        log(f"ERROR: Failed to load INSERT_READY.csv: {e}")
        sys.exit(1)

    # Load existing database
    log(f"Loading existing database from: {DB_PATH}")
    try:
        existing_db = pd.read_csv(DB_PATH, encoding='utf-8-sig')
        initial_count = len(existing_db)
        log(f"Successfully loaded existing database with {initial_count} records")
    except Exception as e:
        log(f"ERROR: Failed to load existing database: {e}")
        sys.exit(1)

    # Display schema comparison
    log("\n" + "="*80)
    log("Schema Comparison")
    log("="*80)
    log(f"INSERT_READY columns: {len(new_data.columns)}")
    log(f"Existing DB columns: {len(existing_db.columns)}")

    # Calculate derived fields for new data
    new_data_enhanced = calculate_derived_fields(new_data)

    # Identify new vs update records
    log("\n" + "="*80)
    log("Analyzing Records for Insertion/Update")
    log("="*80)

    new_records = []
    updated_records = []
    duplicate_records = []

    for idx, new_row in new_data_enhanced.iterrows():
        ticker = new_row['ticker']
        fiscal_year = new_row['fiscal_year']
        period_type = new_row['period_type']

        # Check if record exists
        existing_match = existing_db[
            (existing_db['ticker'] == ticker) &
            (existing_db['fiscal_year'] == fiscal_year) &
            (existing_db['period_type'] == period_type)
        ]

        if len(existing_match) == 0:
            new_records.append(new_row)
            log(f"NEW: Ticker {ticker}, FY {fiscal_year}, {period_type}")
        else:
            # Check if we should update (newer extraction date)
            existing_date = pd.to_datetime(existing_match.iloc[0].get('extraction_date', '2000-01-01'), errors='coerce')
            new_date = pd.to_datetime(new_row['extraction_date'], errors='coerce')

            if pd.notna(new_date) and pd.notna(existing_date) and new_date > existing_date:
                # Update existing record
                existing_db.loc[existing_match.index[0]] = new_row
                updated_records.append(new_row)
                log(f"UPDATE: Ticker {ticker}, FY {fiscal_year}, {period_type} (newer data)")
            else:
                duplicate_records.append(new_row)
                log(f"SKIP: Ticker {ticker}, FY {fiscal_year}, {period_type} (duplicate, not newer)")

    log("\n" + "="*80)
    log("Insertion Summary")
    log("="*80)
    log(f"Total records in INSERT_READY.csv: {len(new_data_enhanced)}")
    log(f"New records to insert: {len(new_records)}")
    log(f"Existing records updated: {len(updated_records)}")
    log(f"Duplicate records skipped: {len(duplicate_records)}")

    # Append new records to existing database
    if new_records:
        log("\nAppending new records to database...")
        new_records_df = pd.DataFrame(new_records)

        # Align columns with existing database
        for col in existing_db.columns:
            if col not in new_records_df.columns:
                new_records_df[col] = np.nan

        # Reorder columns to match existing database
        new_records_df = new_records_df[existing_db.columns]

        # Append to existing database
        updated_db = pd.concat([existing_db, new_records_df], ignore_index=True)
    else:
        updated_db = existing_db

    # Save updated database
    log("\n" + "="*80)
    log("Saving Updated Database")
    log("="*80)

    try:
        # Save with UTF-8 BOM to preserve encoding
        updated_db.to_csv(DB_PATH, index=False, encoding='utf-8-sig')
        final_count = len(updated_db)
        log(f"Successfully saved updated database")
        log(f"Previous record count: {initial_count}")
        log(f"New record count: {final_count}")
        log(f"Net change: +{final_count - initial_count} records")
    except Exception as e:
        log(f"ERROR: Failed to save database: {e}")
        sys.exit(1)

    # Write log to file
    log("\n" + "="*80)
    log("Writing Log File")
    log("="*80)

    try:
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(log_messages))
        log(f"Log file saved to: {LOG_PATH}")
    except Exception as e:
        log(f"WARNING: Failed to save log file: {e}")

    log("\n" + "="*80)
    log("Insertion Complete!")
    log("="*80)

    # Print detailed summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Records processed: {len(new_data_enhanced)}")
    print(f"New records inserted: {len(new_records)}")
    print(f"Existing records updated: {len(updated_records)}")
    print(f"Duplicate records skipped: {len(duplicate_records)}")
    print(f"Database size before: {initial_count}")
    print(f"Database size after: {final_count}")
    print(f"Net change: +{final_count - initial_count}")
    print("="*80)

if __name__ == "__main__":
    main()
