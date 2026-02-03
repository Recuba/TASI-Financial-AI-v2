"""Fast data loader for Neon database using psycopg2.extras.execute_values"""
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import numpy as np

NEON_URL = "postgresql://neondb_owner:npg_mnhJYw3Xb6FG@ep-little-lab-ahi7v65g-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
CSV_PATH = "C:/Users/User/venna-ai/TASI_financials_DB.csv"

def main():
    # Read CSV
    print("Loading CSV...")
    df = pd.read_csv(CSV_PATH)
    print(f"Loaded {len(df)} records")

    # Connect
    print("Connecting to Neon...")
    conn = psycopg2.connect(NEON_URL)
    cur = conn.cursor()

    # Clear existing data
    cur.execute("TRUNCATE TABLE tasi_financials RESTART IDENTITY")
    conn.commit()
    print("Cleared existing data")

    # Column mapping
    db_cols = [
        'ticker', 'company_name', 'company_type', 'sector_gics',
        'report_type', 'fiscal_year', 'fiscal_quarter', 'report_date',
        'revenue', 'gross_profit', 'operating_profit', 'net_income',
        'total_assets', 'total_liabilities', 'total_equity',
        'current_assets', 'current_liabilities', 'cash_and_equivalents',
        'total_debt', 'operating_cash_flow', 'investing_cash_flow',
        'financing_cash_flow', 'free_cash_flow', 'eps',
        'book_value_per_share', 'dividend_per_share', 'shares_outstanding'
    ]

    # Get only columns that exist in CSV
    csv_cols = [c for c in db_cols if c in df.columns]
    print(f"Using columns: {csv_cols}")

    # Prepare data - replace NaN with None
    data = []
    for _, row in df.iterrows():
        values = []
        for col in csv_cols:
            val = row.get(col, None)
            if pd.isna(val):
                values.append(None)
            else:
                values.append(val)
        data.append(tuple(values))

    # Bulk insert using execute_values (much faster)
    cols_str = ', '.join(csv_cols)
    insert_sql = f"INSERT INTO tasi_financials ({cols_str}) VALUES %s"

    print(f"Inserting {len(data)} records...")
    execute_values(cur, insert_sql, data, page_size=1000)
    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM tasi_financials")
    count = cur.fetchone()[0]
    print(f"Successfully loaded {count} records into Neon database")

    # Show sample
    cur.execute("SELECT ticker, company_name, fiscal_year, report_type FROM tasi_financials LIMIT 5")
    print("\nSample records:")
    for row in cur.fetchall():
        print(f"  {row}")

    conn.close()
    print("\nDone!")

if __name__ == "__main__":
    main()
