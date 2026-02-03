"""
TASI Financial Database - Complete Setup Script
Sets up PostgreSQL with pgvector and migrates CSV data
"""

import os
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA_DIR = Path(__file__).parent / "schema"
CSV_PATH = Path(__file__).parent / "TASI_financials_DB.csv"


def get_connection(database_url: str = None, autocommit: bool = False):
    """Create database connection."""
    url = database_url or DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL not set. Copy .env.example to .env and configure it.")

    conn = psycopg2.connect(url)
    if autocommit:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def check_extensions(conn):
    """Check and enable required PostgreSQL extensions."""
    print("\n📦 Checking PostgreSQL extensions...")

    cursor = conn.cursor()

    # Check pgvector
    cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
    if not cursor.fetchone():
        print("   Installing pgvector extension...")
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.commit()
            print("   ✓ pgvector installed")
        except Exception as e:
            print(f"   ⚠ Could not install pgvector: {e}")
            print("   Note: On Neon, pgvector is pre-installed. On local PostgreSQL, install it first.")
    else:
        print("   ✓ pgvector already installed")

    # Check pg_trgm
    cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'")
    if not cursor.fetchone():
        print("   Installing pg_trgm extension...")
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            conn.commit()
            print("   ✓ pg_trgm installed")
        except Exception as e:
            print(f"   ⚠ Could not install pg_trgm: {e}")
    else:
        print("   ✓ pg_trgm already installed")

    cursor.close()


def apply_schema(conn):
    """Apply the database schema."""
    print("\n📐 Applying database schema...")

    schema_file = SCHEMA_DIR / "01_schema.sql"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    cursor = conn.cursor()

    # Read and execute schema
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Split by semicolons and execute each statement
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

    success = 0
    skipped = 0

    for stmt in statements:
        if not stmt or stmt.startswith('--'):
            continue
        try:
            cursor.execute(stmt)
            success += 1
        except psycopg2.errors.DuplicateTable:
            skipped += 1
            conn.rollback()
        except psycopg2.errors.DuplicateObject:
            skipped += 1
            conn.rollback()
        except Exception as e:
            if 'already exists' in str(e).lower():
                skipped += 1
                conn.rollback()
            else:
                print(f"   ⚠ Error: {e}")
                conn.rollback()

    conn.commit()
    print(f"   ✓ Schema applied ({success} statements, {skipped} skipped)")
    cursor.close()


def run_migration(conn):
    """Run the data migration from CSV."""
    print("\n📊 Migrating CSV data...")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    # Import migration module
    sys.path.insert(0, str(SCHEMA_DIR))
    from importlib import import_module

    # We'll run the migration logic inline to use our connection
    import pandas as pd
    from datetime import datetime

    # Load CSV
    print(f"   Loading {CSV_PATH.name}...")
    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
    print(f"   Loaded {len(df)} records")

    cursor = conn.cursor()

    # Caches
    sectors_cache = {}
    companies_cache = {}
    periods_cache = {}

    def clean_numeric(value):
        if pd.isna(value) or value == "" or value is None:
            return None
        if isinstance(value, str):
            value = value.replace("%", "").replace(",", "").strip()
            if not value:
                return None
        try:
            return float(value)
        except:
            return None

    def clean_boolean(value):
        if pd.isna(value):
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.upper() in ("TRUE", "YES", "1", "T")
        return bool(value)

    def parse_date(date_str):
        if pd.isna(date_str) or not date_str:
            return None
        for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(str(date_str), fmt)
            except:
                continue
        return None

    def get_quarter(period_end, period_type):
        if period_type == "Annual":
            return "FY"
        month = period_end.month
        if month <= 3: return "Q1"
        elif month <= 6: return "Q2"
        elif month <= 9: return "Q3"
        else: return "Q4"

    def get_or_create_sector(name):
        if not name or pd.isna(name):
            return None
        name = str(name).strip()
        if not name:
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
        size_category = str(row.get("size_category", "")).strip() or None

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
            period_end = datetime(fiscal_year, 12, 31)
        else:
            quarter_starts = {"Q1": 1, "Q2": 4, "Q3": 7, "Q4": 10}
            quarter_ends = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}
            period_start = datetime(fiscal_year, quarter_starts.get(fiscal_quarter, 1), 1)
            end_month = quarter_ends.get(fiscal_quarter, 12)
            if end_month == 12:
                period_end = datetime(fiscal_year, 12, 31)
            else:
                period_end = datetime(fiscal_year, end_month + 1, 1) - pd.Timedelta(days=1)

        period_label = f"FY{fiscal_year}" if period_type == "Annual" else f"{fiscal_quarter} {fiscal_year}"

        cursor.execute("""
            INSERT INTO fiscal_periods (fiscal_year, fiscal_quarter, period_type, period_start, period_end, period_label)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING period_id
        """, (fiscal_year, fiscal_quarter, period_type, period_start, period_end, period_label))

        period_id = cursor.fetchone()[0]
        periods_cache[cache_key] = period_id
        return period_id

    # Process records
    success = 0
    errors = 0

    for idx, row in df.iterrows():
        try:
            company_id = get_or_create_company(row)
            period_id = get_or_create_period(row)
            filing_id = str(row.get("filing_id", "")).strip() or None

            # Check for existing
            cursor.execute(
                "SELECT statement_id FROM financial_statements WHERE company_id = %s AND period_id = %s",
                (company_id, period_id)
            )
            existing = cursor.fetchone()
            if existing:
                statement_id = existing[0]
            else:
                # Insert financial statement
                cursor.execute("""
                    INSERT INTO financial_statements (
                        company_id, period_id, filing_id,
                        revenue, cost_of_sales, gross_profit, operating_profit, net_profit, interest_expense,
                        total_assets, total_equity, total_liabilities, current_assets, current_liabilities,
                        inventory, receivables, operating_cash_flow, capex, free_cash_flow, working_capital,
                        data_quality_score, is_latest
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING statement_id
                """, (
                    company_id, period_id, filing_id,
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

            # Insert metrics (if not exists)
            cursor.execute("SELECT 1 FROM financial_metrics WHERE statement_id = %s", (statement_id,))
            if not cursor.fetchone():
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
                    int(clean_numeric(row.get("profitability_score")) or 0) or None,
                    str(row.get("profit_status", "")).strip() or None,
                    str(row.get("liquidity_status", "")).strip() or None,
                    str(row.get("leverage_status", "")).strip() or None,
                    str(row.get("roe_status", "")).strip() or None,
                    clean_boolean(row.get("has_cogs")),
                    clean_boolean(row.get("has_operating_profit")),
                    clean_boolean(row.get("has_cash_flow"))
                ))

            success += 1

            if (idx + 1) % 500 == 0:
                conn.commit()
                print(f"   Processed {idx + 1}/{len(df)} records...")

        except Exception as e:
            errors += 1
            conn.rollback()
            if errors <= 5:
                print(f"   ⚠ Error on row {idx}: {e}")

    conn.commit()
    cursor.close()

    print(f"   ✓ Migration complete: {success} records, {errors} errors")
    print(f"   ✓ Created {len(sectors_cache)} sectors, {len(companies_cache)} companies, {len(periods_cache)} periods")


def refresh_view(conn):
    """Refresh the materialized view."""
    print("\n🔄 Refreshing materialized view...")
    cursor = conn.cursor()
    try:
        cursor.execute("REFRESH MATERIALIZED VIEW company_financials")
        conn.commit()
        print("   ✓ View refreshed")
    except Exception as e:
        print(f"   ⚠ Could not refresh view: {e}")
    cursor.close()


def validate_setup(conn):
    """Validate the database setup."""
    print("\n✅ Validating setup...")

    cursor = conn.cursor()

    # Count records
    tables = [
        ("sectors", "sector_id"),
        ("companies", "company_id"),
        ("fiscal_periods", "period_id"),
        ("financial_statements", "statement_id"),
        ("financial_metrics", "metric_id"),
    ]

    print("   Table record counts:")
    for table, pk in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     {table}: {count:,}")

    # Test materialized view
    cursor.execute("SELECT COUNT(*) FROM company_financials")
    view_count = cursor.fetchone()[0]
    print(f"     company_financials (view): {view_count:,}")

    # Sample query
    print("\n   Sample data (top 5 companies by ROE):")
    cursor.execute("""
        SELECT ticker, company_name, sector, roe_percent
        FROM company_financials
        WHERE is_latest = TRUE AND is_annual = TRUE
        ORDER BY roe_percent DESC NULLS LAST
        LIMIT 5
    """)

    for row in cursor.fetchall():
        print(f"     {row[0]}: {row[1][:30]:<30} | {row[2] or 'N/A':<15} | ROE: {row[3] or 0:.1f}%")

    cursor.close()
    print("\n   ✓ Validation complete!")


def main():
    """Run the complete setup."""
    print("=" * 60)
    print("🏦 TASI Financial Database Setup")
    print("=" * 60)

    if not DATABASE_URL:
        print("\n❌ ERROR: DATABASE_URL not set!")
        print("   1. Copy .env.example to .env")
        print("   2. Add your PostgreSQL connection string")
        print("   3. Run this script again")
        sys.exit(1)

    # Mask password in URL for display
    display_url = DATABASE_URL
    if '@' in display_url:
        parts = display_url.split('@')
        display_url = parts[0].split(':')[0] + ':****@' + parts[1]
    print(f"\n📡 Connecting to: {display_url}")

    try:
        conn = get_connection()
        print("   ✓ Connected successfully")

        check_extensions(conn)
        apply_schema(conn)
        run_migration(conn)
        refresh_view(conn)
        validate_setup(conn)

        conn.close()

        print("\n" + "=" * 60)
        print("🎉 Setup complete! Your database is ready for Vanna AI.")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Set VANNA_API_KEY in your .env file")
        print("  2. Run: python schema/03_vanna_training.py")
        print("  3. Start querying with natural language!")

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
