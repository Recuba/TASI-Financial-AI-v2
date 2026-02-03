"""
TASI Financial Database - Data Migration Only
Migrates CSV data to already-created PostgreSQL schema
"""

import os
import sys
import io
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import pandas as pd
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CSV_PATH = Path(__file__).parent / "TASI_financials_DB.csv"


def clean_numeric(value):
    """Clean and convert numeric values."""
    if pd.isna(value) or value == "" or value is None:
        return None
    if isinstance(value, str):
        value = value.replace("%", "").replace(",", "").strip()
        if not value:
            return None
    try:
        result = float(value)
        # Check for NaN
        if pd.isna(result):
            return None
        return result
    except:
        return None


def clean_boolean(value):
    """Convert various boolean representations."""
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.upper() in ("TRUE", "YES", "1", "T")
    return bool(value)


def clean_status(value, valid_values):
    """Clean status fields, returning None if invalid."""
    if pd.isna(value) or value is None:
        return None
    val = str(value).strip()
    if val.lower() in ('nan', 'n/a', '', 'none'):
        return None
    if val in valid_values:
        return val
    return None


def parse_date(date_str):
    """Parse various date formats."""
    if pd.isna(date_str) or not date_str:
        return None
    for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]:
        try:
            return datetime.strptime(str(date_str), fmt)
        except:
            continue
    return None


def get_quarter(period_end, period_type):
    """Determine fiscal quarter from date."""
    if period_type == "Annual":
        return "FY"
    month = period_end.month
    if month <= 3: return "Q1"
    elif month <= 6: return "Q2"
    elif month <= 9: return "Q3"
    else: return "Q4"


def main():
    print("=" * 60)
    print("TASI Financial Database - Data Migration")
    print("=" * 60)

    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not set!")
        sys.exit(1)

    print(f"\nConnecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True  # Commit each statement immediately
    cursor = conn.cursor()
    print("Connected!")

    # Load CSV
    print(f"\nLoading {CSV_PATH.name}...")
    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    print(f"Loaded {len(df)} records")

    # Caches
    sectors_cache = {}
    companies_cache = {}
    periods_cache = {}

    # Valid status values
    PROFIT_STATUS = ('Profit', 'Loss', 'N/A')
    LIQUIDITY_STATUS = ('Strong', 'Moderate', 'Weak', 'Critical')
    LEVERAGE_STATUS = ('Low', 'Moderate', 'High', 'Critical')
    ROE_STATUS = ('Excellent', 'Good', 'Average', 'Weak', 'Negative', 'N/A')

    def get_or_create_sector(name):
        if not name or pd.isna(name):
            return None
        name = str(name).strip()
        if not name or name.lower() == 'nan':
            return None
        if name in sectors_cache:
            return sectors_cache[name]

        cursor.execute("SELECT sector_id FROM sectors WHERE sector_name = %s", (name,))
        row = cursor.fetchone()
        if row:
            sectors_cache[name] = row[0]
            return row[0]

        cursor.execute(
            "INSERT INTO sectors (sector_name, sector_code) VALUES (%s, %s) RETURNING sector_id",
            (name, name.upper().replace(" ", "_")[:20])
        )
        sector_id = cursor.fetchone()[0]
        sectors_cache[name] = sector_id
        return sector_id

    def get_or_create_company(row):
        ticker = str(row.get("ticker", "")).strip()
        # Clean ticker - remove .0 if present
        if ticker.endswith('.0'):
            ticker = ticker[:-2]

        if ticker in companies_cache:
            return companies_cache[ticker]

        cursor.execute("SELECT company_id FROM companies WHERE ticker = %s", (ticker,))
        result = cursor.fetchone()
        if result:
            companies_cache[ticker] = result[0]
            return result[0]

        sector_name = row.get("sector_derived") or row.get("sector_gics")
        sector_id = get_or_create_sector(sector_name)
        company_name = str(row.get("company_name", ticker)).strip()
        company_type = str(row.get("company_type", "")).strip() or None
        if company_type and company_type.lower() == 'nan':
            company_type = None
        size_category = str(row.get("size_category", "")).strip() or None
        if size_category and size_category.lower() == 'nan':
            size_category = None

        cursor.execute("""
            INSERT INTO companies (ticker, company_name, sector_id, company_type, size_category)
            VALUES (%s, %s, %s, %s, %s) RETURNING company_id
        """, (ticker, company_name, sector_id, company_type, size_category))

        company_id = cursor.fetchone()[0]
        companies_cache[ticker] = company_id
        return company_id

    def get_or_create_period(row):
        fiscal_year = int(row.get("fiscal_year", 0))
        period_type = str(row.get("period_type", "")).strip()
        period_end = parse_date(row.get("period_end"))

        if not period_end:
            period_end = datetime(fiscal_year, 12, 31) if period_type == "Annual" else datetime(fiscal_year, 6, 30)

        fiscal_quarter = get_quarter(period_end, period_type)
        cache_key = f"{fiscal_year}_{fiscal_quarter}"

        if cache_key in periods_cache:
            return periods_cache[cache_key]

        cursor.execute(
            "SELECT period_id FROM fiscal_periods WHERE fiscal_year = %s AND fiscal_quarter = %s",
            (fiscal_year, fiscal_quarter)
        )
        result = cursor.fetchone()
        if result:
            periods_cache[cache_key] = result[0]
            return result[0]

        if period_type == "Annual":
            period_start = datetime(fiscal_year, 1, 1)
            period_end_dt = datetime(fiscal_year, 12, 31)
        else:
            quarter_starts = {"Q1": 1, "Q2": 4, "Q3": 7, "Q4": 10}
            quarter_ends = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}
            period_start = datetime(fiscal_year, quarter_starts.get(fiscal_quarter, 1), 1)
            end_month = quarter_ends.get(fiscal_quarter, 12)
            if end_month == 12:
                period_end_dt = datetime(fiscal_year, 12, 31)
            else:
                period_end_dt = datetime(fiscal_year, end_month + 1, 1) - pd.Timedelta(days=1)

        period_label = f"FY{fiscal_year}" if period_type == "Annual" else f"{fiscal_quarter} {fiscal_year}"

        cursor.execute("""
            INSERT INTO fiscal_periods (fiscal_year, fiscal_quarter, period_type, period_start, period_end, period_label)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING period_id
        """, (fiscal_year, fiscal_quarter, period_type, period_start, period_end_dt, period_label))

        period_id = cursor.fetchone()[0]
        periods_cache[cache_key] = period_id
        return period_id

    # Process records
    print("\nMigrating data...")
    success = 0
    errors = 0
    skipped = 0

    for idx, row in df.iterrows():
        try:
            company_id = get_or_create_company(row)
            period_id = get_or_create_period(row)

            # Check for existing
            cursor.execute(
                "SELECT statement_id FROM financial_statements WHERE company_id = %s AND period_id = %s",
                (company_id, period_id)
            )
            existing = cursor.fetchone()
            if existing:
                skipped += 1
                continue

            # Insert financial statement
            cursor.execute("""
                INSERT INTO financial_statements (
                    company_id, period_id,
                    revenue, cost_of_sales, gross_profit, operating_profit, net_profit, interest_expense,
                    total_assets, total_equity, total_liabilities, current_assets, current_liabilities,
                    inventory, receivables, operating_cash_flow, capex, free_cash_flow, working_capital,
                    data_quality_score, is_latest
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING statement_id
            """, (
                company_id, period_id,
                clean_numeric(row.get("revenue")),
                clean_numeric(row.get("cost_of_sales")),
                clean_numeric(row.get("gross_profit")),
                clean_numeric(row.get("operating_profit")),
                clean_numeric(row.get("net_profit")),
                clean_numeric(row.get("interest_expense")),
                clean_numeric(row.get("total_assets")),
                clean_numeric(row.get("total_equity")),
                clean_numeric(row.get("total_liabilities")),
                clean_numeric(row.get("current_assets")),
                clean_numeric(row.get("current_liabilities")),
                clean_numeric(row.get("inventory")),
                clean_numeric(row.get("receivables")),
                clean_numeric(row.get("operating_cash_flow")),
                clean_numeric(row.get("capex")),
                clean_numeric(row.get("free_cash_flow")),
                clean_numeric(row.get("working_capital")),
                int(clean_numeric(row.get("data_quality_score")) or 0),
                clean_boolean(row.get("is_latest"))
            ))
            statement_id = cursor.fetchone()[0]

            # Insert metrics
            profitability_score = clean_numeric(row.get("profitability_score"))
            if profitability_score is not None:
                profitability_score = int(profitability_score)
                if profitability_score == 0:
                    profitability_score = None

            cursor.execute("""
                INSERT INTO financial_metrics (
                    statement_id, return_on_equity, return_on_assets, gross_margin, operating_margin, net_margin,
                    current_ratio, quick_ratio, debt_to_equity, debt_to_assets, interest_coverage_ratio,
                    asset_turnover, inventory_turnover, days_sales_outstanding, profitability_score,
                    profit_status, liquidity_status, leverage_status, roe_status,
                    has_cogs, has_operating_profit, has_cash_flow
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                statement_id,
                clean_numeric(row.get("return_on_equity")) or clean_numeric(row.get("roe_decimal")),
                clean_numeric(row.get("return_on_assets")) or clean_numeric(row.get("roa_decimal")),
                clean_numeric(row.get("gross_margin")) or clean_numeric(row.get("gross_margin_decimal")),
                clean_numeric(row.get("operating_margin")) or clean_numeric(row.get("operating_margin_decimal")),
                clean_numeric(row.get("net_margin")) or clean_numeric(row.get("net_margin_decimal")),
                clean_numeric(row.get("current_ratio")),
                clean_numeric(row.get("quick_ratio")),
                clean_numeric(row.get("debt_to_equity")),
                clean_numeric(row.get("debt_to_assets")),
                clean_numeric(row.get("interest_coverage_ratio")),
                clean_numeric(row.get("asset_turnover")),
                clean_numeric(row.get("inventory_turnover")),
                clean_numeric(row.get("days_sales_outstanding")),
                profitability_score,
                clean_status(row.get("profit_status"), PROFIT_STATUS),
                clean_status(row.get("liquidity_status"), LIQUIDITY_STATUS),
                clean_status(row.get("leverage_status"), LEVERAGE_STATUS),
                clean_status(row.get("roe_status"), ROE_STATUS),
                clean_boolean(row.get("has_cogs")),
                clean_boolean(row.get("has_operating_profit")),
                clean_boolean(row.get("has_cash_flow"))
            ))

            success += 1

            if (idx + 1) % 500 == 0:
                print(f"  Processed {idx + 1}/{len(df)} records...")

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  Error on row {idx}: {e}")

    print(f"\nMigration complete:")
    print(f"  - Success: {success:,}")
    print(f"  - Skipped: {skipped:,}")
    print(f"  - Errors: {errors}")
    print(f"  - Sectors: {len(sectors_cache)}")
    print(f"  - Companies: {len(companies_cache)}")
    print(f"  - Periods: {len(periods_cache)}")

    # Refresh materialized view
    print("\nRefreshing materialized view...")
    try:
        cursor.execute("REFRESH MATERIALIZED VIEW company_financials")
        print("View refreshed!")
    except Exception as e:
        print(f"Could not refresh view: {e}")

    # Validate
    print("\nValidation:")
    for table in ["sectors", "companies", "fiscal_periods", "financial_statements", "financial_metrics"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count:,}")

    cursor.execute("SELECT COUNT(*) FROM company_financials")
    print(f"  company_financials (view): {cursor.fetchone()[0]:,}")

    # Sample query
    print("\nTop 5 companies by ROE:")
    cursor.execute("""
        SELECT ticker, company_name, sector, roe_percent
        FROM company_financials
        WHERE is_latest = TRUE AND is_annual = TRUE AND roe_percent IS NOT NULL
        ORDER BY roe_percent DESC NULLS LAST
        LIMIT 5
    """)
    for row in cursor.fetchall():
        roe = f"{row[3]:.1f}%" if row[3] else "N/A"
        print(f"  {row[0]}: {row[1][:35]:<35} | ROE: {roe}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print("Database setup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
