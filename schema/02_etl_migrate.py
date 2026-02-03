"""
ETL Script: Migrate TASI Financial CSV to PostgreSQL + pgvector
Optimized for Vanna AI natural language queries
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import execute_values
import os

# Configuration
CSV_PATH = "../TASI_financials_DB.csv"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/tasi_financials")


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse various date formats from the CSV."""
    if pd.isna(date_str) or not date_str:
        return None

    formats = ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue
    return None


def clean_numeric(value) -> Optional[float]:
    """Clean and convert numeric values."""
    if pd.isna(value) or value == "" or value is None:
        return None

    if isinstance(value, str):
        # Remove percentage signs and commas
        value = value.replace("%", "").replace(",", "").strip()
        if not value:
            return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def clean_boolean(value) -> bool:
    """Convert various boolean representations."""
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.upper() in ("TRUE", "YES", "1", "T")
    return bool(value)


def determine_quarter_from_date(period_end: datetime, period_type: str) -> str:
    """Determine fiscal quarter from period end date."""
    if period_type == "Annual":
        return "FY"

    month = period_end.month
    if month in [1, 2, 3]:
        return "Q1"  # Jan-Mar -> Q1
    elif month in [4, 5, 6]:
        return "Q2"  # Apr-Jun -> Q2
    elif month in [7, 8, 9]:
        return "Q3"  # Jul-Sep -> Q3
    else:
        return "Q4"  # Oct-Dec -> Q4


class TASIDataMigrator:
    def __init__(self, database_url: str):
        self.conn = psycopg2.connect(database_url)
        self.cursor = self.conn.cursor()

        # Caches for lookups
        self.sectors_cache = {}
        self.companies_cache = {}
        self.periods_cache = {}

    def close(self):
        self.cursor.close()
        self.conn.close()

    def load_csv(self, csv_path: str) -> pd.DataFrame:
        """Load and preprocess the CSV file."""
        print(f"Loading CSV: {csv_path}")
        df = pd.read_csv(csv_path, encoding='utf-8-sig')  # Handle BOM
        print(f"Loaded {len(df)} records with {len(df.columns)} columns")
        return df

    def get_or_create_sector(self, sector_name: str) -> Optional[int]:
        """Get or create a sector and return its ID."""
        if not sector_name or pd.isna(sector_name):
            return None

        sector_name = str(sector_name).strip()
        if not sector_name:
            return None

        if sector_name in self.sectors_cache:
            return self.sectors_cache[sector_name]

        # Check if exists
        self.cursor.execute(
            "SELECT sector_id FROM sectors WHERE sector_name = %s",
            (sector_name,)
        )
        result = self.cursor.fetchone()

        if result:
            self.sectors_cache[sector_name] = result[0]
            return result[0]

        # Create new
        self.cursor.execute(
            "INSERT INTO sectors (sector_name, sector_code) VALUES (%s, %s) RETURNING sector_id",
            (sector_name, sector_name.upper().replace(" ", "_")[:20])
        )
        sector_id = self.cursor.fetchone()[0]
        self.sectors_cache[sector_name] = sector_id
        return sector_id

    def get_or_create_company(self, row: pd.Series) -> int:
        """Get or create a company and return its ID."""
        ticker = str(row.get("ticker", "")).strip()

        if ticker in self.companies_cache:
            return self.companies_cache[ticker]

        # Check if exists
        self.cursor.execute(
            "SELECT company_id FROM companies WHERE ticker = %s",
            (ticker,)
        )
        result = self.cursor.fetchone()

        if result:
            self.companies_cache[ticker] = result[0]
            return result[0]

        # Get sector
        sector_name = row.get("sector_derived") or row.get("sector_gics")
        sector_id = self.get_or_create_sector(sector_name)

        # Create new company
        company_name = str(row.get("company_name", ticker)).strip()
        company_type = str(row.get("company_type", "")).strip() or None
        size_category = str(row.get("size_category", "")).strip() or None

        self.cursor.execute("""
            INSERT INTO companies (ticker, company_name, sector_id, company_type, size_category)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING company_id
        """, (ticker, company_name, sector_id, company_type, size_category))

        company_id = self.cursor.fetchone()[0]
        self.companies_cache[ticker] = company_id
        return company_id

    def get_or_create_period(self, row: pd.Series) -> int:
        """Get or create a fiscal period and return its ID."""
        fiscal_year = int(row.get("fiscal_year", 0))
        period_type = str(row.get("period_type", "")).strip()
        period_end_str = row.get("period_end")

        period_end = parse_date(period_end_str)
        if not period_end:
            # Fallback: use year-end for annual, mid-year for quarterly
            if period_type == "Annual":
                period_end = datetime(fiscal_year, 12, 31)
            else:
                period_end = datetime(fiscal_year, 6, 30)

        fiscal_quarter = determine_quarter_from_date(period_end, period_type)

        cache_key = f"{fiscal_year}_{fiscal_quarter}"
        if cache_key in self.periods_cache:
            return self.periods_cache[cache_key]

        # Check if exists
        self.cursor.execute(
            "SELECT period_id FROM fiscal_periods WHERE fiscal_year = %s AND fiscal_quarter = %s",
            (fiscal_year, fiscal_quarter)
        )
        result = self.cursor.fetchone()

        if result:
            self.periods_cache[cache_key] = result[0]
            return result[0]

        # Calculate period start
        if period_type == "Annual":
            period_start = datetime(fiscal_year, 1, 1)
            period_end = datetime(fiscal_year, 12, 31)
        else:
            quarter_starts = {"Q1": 1, "Q2": 4, "Q3": 7, "Q4": 10}
            quarter_ends = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}
            start_month = quarter_starts.get(fiscal_quarter, 1)
            end_month = quarter_ends.get(fiscal_quarter, 12)
            period_start = datetime(fiscal_year, start_month, 1)

            # Calculate last day of end month
            if end_month == 12:
                period_end = datetime(fiscal_year, 12, 31)
            else:
                period_end = datetime(fiscal_year, end_month + 1, 1) - pd.Timedelta(days=1)

        period_label = f"FY{fiscal_year}" if period_type == "Annual" else f"{fiscal_quarter} {fiscal_year}"

        self.cursor.execute("""
            INSERT INTO fiscal_periods (fiscal_year, fiscal_quarter, period_type, period_start, period_end, period_label)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING period_id
        """, (fiscal_year, fiscal_quarter, period_type, period_start, period_end, period_label))

        period_id = self.cursor.fetchone()[0]
        self.periods_cache[cache_key] = period_id
        return period_id

    def insert_financial_statement(self, row: pd.Series, company_id: int, period_id: int) -> Optional[int]:
        """Insert a financial statement record."""
        filing_id = str(row.get("filing_id", "")).strip() or None

        # Check for duplicate
        if filing_id:
            self.cursor.execute(
                "SELECT statement_id FROM financial_statements WHERE filing_id = %s",
                (filing_id,)
            )
            existing = self.cursor.fetchone()
            if existing:
                return existing[0]

        # Also check by company + period
        self.cursor.execute(
            "SELECT statement_id FROM financial_statements WHERE company_id = %s AND period_id = %s",
            (company_id, period_id)
        )
        existing = self.cursor.fetchone()
        if existing:
            return existing[0]

        statement_data = {
            "company_id": company_id,
            "period_id": period_id,
            "filing_id": filing_id,
            "revenue": clean_numeric(row.get("revenue")),
            "cost_of_sales": clean_numeric(row.get("cost_of_sales")),
            "gross_profit": clean_numeric(row.get("gross_profit")),
            "operating_profit": clean_numeric(row.get("operating_profit")),
            "net_profit": clean_numeric(row.get("net_profit")),
            "interest_expense": clean_numeric(row.get("interest_expense")),
            "total_assets": clean_numeric(row.get("total_assets")),
            "total_equity": clean_numeric(row.get("total_equity")),
            "total_liabilities": clean_numeric(row.get("total_liabilities")),
            "current_assets": clean_numeric(row.get("current_assets")),
            "current_liabilities": clean_numeric(row.get("current_liabilities")),
            "inventory": clean_numeric(row.get("inventory")),
            "receivables": clean_numeric(row.get("receivables")),
            "operating_cash_flow": clean_numeric(row.get("operating_cash_flow")),
            "capex": clean_numeric(row.get("capex")),
            "free_cash_flow": clean_numeric(row.get("free_cash_flow")),
            "working_capital": clean_numeric(row.get("working_capital")),
            "data_quality_score": int(clean_numeric(row.get("data_quality_score")) or 0),
            "is_latest": clean_boolean(row.get("is_latest")),
        }

        columns = list(statement_data.keys())
        values = list(statement_data.values())
        placeholders = ", ".join(["%s"] * len(columns))

        self.cursor.execute(f"""
            INSERT INTO financial_statements ({", ".join(columns)})
            VALUES ({placeholders})
            RETURNING statement_id
        """, values)

        return self.cursor.fetchone()[0]

    def insert_financial_metrics(self, row: pd.Series, statement_id: int):
        """Insert financial metrics for a statement."""
        # Check if already exists
        self.cursor.execute(
            "SELECT metric_id FROM financial_metrics WHERE statement_id = %s",
            (statement_id,)
        )
        if self.cursor.fetchone():
            return

        metrics_data = {
            "statement_id": statement_id,
            "return_on_equity": clean_numeric(row.get("return_on_equity")) or clean_numeric(row.get("roe_decimal")),
            "return_on_assets": clean_numeric(row.get("return_on_assets")) or clean_numeric(row.get("roa_decimal")),
            "gross_margin": clean_numeric(row.get("gross_margin")) or clean_numeric(row.get("gross_margin_decimal")),
            "operating_margin": clean_numeric(row.get("operating_margin")) or clean_numeric(row.get("operating_margin_decimal")),
            "net_margin": clean_numeric(row.get("net_margin")) or clean_numeric(row.get("net_margin_decimal")),
            "current_ratio": clean_numeric(row.get("current_ratio")),
            "quick_ratio": clean_numeric(row.get("quick_ratio")),
            "debt_to_equity": clean_numeric(row.get("debt_to_equity")),
            "debt_to_assets": clean_numeric(row.get("debt_to_assets")),
            "interest_coverage_ratio": clean_numeric(row.get("interest_coverage_ratio")),
            "asset_turnover": clean_numeric(row.get("asset_turnover")),
            "inventory_turnover": clean_numeric(row.get("inventory_turnover")),
            "days_sales_outstanding": clean_numeric(row.get("days_sales_outstanding")),
            "profitability_score": int(clean_numeric(row.get("profitability_score")) or 0) or None,
            "profit_status": str(row.get("profit_status", "")).strip() or None,
            "liquidity_status": str(row.get("liquidity_status", "")).strip() or None,
            "leverage_status": str(row.get("leverage_status", "")).strip() or None,
            "roe_status": str(row.get("roe_status", "")).strip() or None,
            "has_cogs": clean_boolean(row.get("has_cogs")),
            "has_operating_profit": clean_boolean(row.get("has_operating_profit")),
            "has_cash_flow": clean_boolean(row.get("has_cash_flow")),
        }

        columns = list(metrics_data.keys())
        values = list(metrics_data.values())
        placeholders = ", ".join(["%s"] * len(columns))

        self.cursor.execute(f"""
            INSERT INTO financial_metrics ({", ".join(columns)})
            VALUES ({placeholders})
        """, values)

    def migrate(self, csv_path: str):
        """Run the full migration."""
        df = self.load_csv(csv_path)

        total = len(df)
        success = 0
        errors = 0

        print(f"Starting migration of {total} records...")

        for idx, row in df.iterrows():
            try:
                # Create/get dimension records
                company_id = self.get_or_create_company(row)
                period_id = self.get_or_create_period(row)

                # Insert fact records
                statement_id = self.insert_financial_statement(row, company_id, period_id)
                if statement_id:
                    self.insert_financial_metrics(row, statement_id)

                success += 1

                if (idx + 1) % 500 == 0:
                    self.conn.commit()
                    print(f"  Processed {idx + 1}/{total} records...")

            except Exception as e:
                errors += 1
                print(f"  Error on row {idx}: {e}")
                if errors > 100:
                    print("Too many errors, aborting!")
                    break

        # Final commit
        self.conn.commit()

        print(f"\nMigration complete:")
        print(f"  - Success: {success}")
        print(f"  - Errors: {errors}")
        print(f"  - Sectors: {len(self.sectors_cache)}")
        print(f"  - Companies: {len(self.companies_cache)}")
        print(f"  - Periods: {len(self.periods_cache)}")

    def refresh_materialized_view(self):
        """Refresh the materialized view after migration."""
        print("Refreshing materialized view...")
        self.cursor.execute("REFRESH MATERIALIZED VIEW company_financials;")
        self.conn.commit()
        print("Done!")


def main():
    """Main entry point."""
    print("=" * 60)
    print("TASI Financial Database Migration")
    print("=" * 60)

    migrator = TASIDataMigrator(DATABASE_URL)

    try:
        migrator.migrate(CSV_PATH)
        migrator.refresh_materialized_view()
    finally:
        migrator.close()

    print("\nMigration completed successfully!")


if __name__ == "__main__":
    main()
