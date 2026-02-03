"""
Financial Data Extraction Validation Script
============================================
Validates the integrity and quality of extracted financial data
after database insertion.

Author: QA Engineering Team
Date: 2026-02-03
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()


class DataValidator:
    """Validates extracted financial data against database"""

    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.conn = None
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            print("[OK] Database connection established")
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """Execute query and return results"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Query error: {e}")
            return None

    def validate_record_counts(self):
        """Validate total record counts match expectations"""
        print("\n" + "="*60)
        print("PHASE 1: Record Count Validation")
        print("="*60)

        # Total records
        result = self.execute_query("SELECT COUNT(*) as total FROM financial_data")
        if result:
            total = result[0]['total']
            print(f"\nTotal records in database: {total}")

            # Expected: 33 new records (from validation report)
            # Plus any existing historical records
            if total >= 33:
                self.validation_results['passed'].append(
                    f"Record count validation: {total} records found (≥33 expected)"
                )
            else:
                self.validation_results['failed'].append(
                    f"Record count too low: {total} (expected ≥33)"
                )

        # Records by fiscal year
        result = self.execute_query("""
            SELECT fiscal_year, COUNT(*) as count
            FROM financial_data
            GROUP BY fiscal_year
            ORDER BY fiscal_year
        """)

        if result:
            print("\nRecords by Fiscal Year:")
            print(f"{'Year':<10} {'Count':<10}")
            print("-" * 20)
            fy_2024_count = 0
            for row in result:
                print(f"{row['fiscal_year']:<10} {row['count']:<10}")
                if row['fiscal_year'] == 2024:
                    fy_2024_count = row['count']

            if fy_2024_count == 33:
                self.validation_results['passed'].append(
                    f"FY2024 record count: {fy_2024_count} (exact match)"
                )
            elif fy_2024_count >= 30:
                self.validation_results['warnings'].append(
                    f"FY2024 record count: {fy_2024_count} (expected 33)"
                )
            else:
                self.validation_results['failed'].append(
                    f"FY2024 record count too low: {fy_2024_count} (expected 33)"
                )

        # Records by sector for 2024
        result = self.execute_query("""
            SELECT sector, COUNT(*) as count
            FROM financial_data
            WHERE fiscal_year = 2024
            GROUP BY sector
            ORDER BY sector
        """)

        if result:
            print("\nFY2024 Records by Sector:")
            print(f"{'Sector':<20} {'Count':<10} {'Expected':<10}")
            print("-" * 40)

            expected_counts = {
                'Banks': 6,
                'Industrial': 13,
                'Other': 14  # Could be various sector names
            }

            for row in result:
                sector = row['sector']
                count = row['count']
                expected = expected_counts.get(sector, '?')
                print(f"{sector:<20} {count:<10} {expected:<10}")

    def validate_data_integrity(self):
        """Validate data integrity constraints"""
        print("\n" + "="*60)
        print("PHASE 2: Data Integrity Validation")
        print("="*60)

        # Check for NULL in critical fields
        critical_fields = [
            'ticker', 'company_name', 'fiscal_year',
            'total_assets', 'total_revenue'
        ]

        for field in critical_fields:
            result = self.execute_query(f"""
                SELECT COUNT(*) as null_count
                FROM financial_data
                WHERE fiscal_year = 2024 AND {field} IS NULL
            """)

            if result and result[0]['null_count'] > 0:
                self.validation_results['failed'].append(
                    f"NULL values found in {field}: {result[0]['null_count']} records"
                )
                print(f"[X] {field}: {result[0]['null_count']} NULL values")
            else:
                print(f"[OK] {field}: No NULL values")
                self.validation_results['passed'].append(f"{field} integrity check")

        # Check for duplicate records (same ticker + fiscal_year)
        result = self.execute_query("""
            SELECT ticker, fiscal_year, COUNT(*) as dup_count
            FROM financial_data
            WHERE fiscal_year = 2024
            GROUP BY ticker, fiscal_year
            HAVING COUNT(*) > 1
        """)

        if result and len(result) > 0:
            print(f"\n[X] Duplicate records found: {len(result)}")
            for row in result:
                print(f"  - Ticker {row['ticker']}, FY{row['fiscal_year']}: {row['dup_count']} copies")
                self.validation_results['failed'].append(
                    f"Duplicate: {row['ticker']} FY{row['fiscal_year']}"
                )
        else:
            print("\n[OK] No duplicate records found")
            self.validation_results['passed'].append("No duplicate records")

    def validate_balance_sheet(self):
        """Validate balance sheet equation: Assets = Liabilities + Equity"""
        print("\n" + "="*60)
        print("PHASE 3: Balance Sheet Validation")
        print("="*60)

        result = self.execute_query("""
            SELECT
                ticker,
                company_name,
                total_assets,
                total_liabilities,
                total_equity,
                ABS(total_assets - (total_liabilities + total_equity)) as variance,
                CASE
                    WHEN total_assets > 0 THEN
                        ABS(total_assets - (total_liabilities + total_equity)) / total_assets * 100
                    ELSE 0
                END as variance_pct
            FROM financial_data
            WHERE fiscal_year = 2024
                AND total_assets IS NOT NULL
                AND total_liabilities IS NOT NULL
                AND total_equity IS NOT NULL
        """)

        if result:
            print(f"\nChecking {len(result)} records...")
            failed_bs = 0
            tolerance = 5.0  # 5% tolerance

            for row in result:
                if row['variance_pct'] > tolerance:
                    failed_bs += 1
                    print(f"[X] {row['ticker']} ({row['company_name']}): {row['variance_pct']:.2f}% variance")
                    self.validation_results['failed'].append(
                        f"Balance sheet variance: {row['ticker']} ({row['variance_pct']:.2f}%)"
                    )

            passed_bs = len(result) - failed_bs
            print(f"\n[OK] {passed_bs}/{len(result)} records passed balance sheet validation")

            if failed_bs == 0:
                self.validation_results['passed'].append(
                    f"All {len(result)} records passed balance sheet validation"
                )

    def validate_data_quality(self):
        """Validate data quality metrics"""
        print("\n" + "="*60)
        print("PHASE 4: Data Quality Metrics")
        print("="*60)

        # Check for negative equity (potential issues)
        result = self.execute_query("""
            SELECT ticker, company_name, total_equity
            FROM financial_data
            WHERE fiscal_year = 2024 AND total_equity < 0
        """)

        if result and len(result) > 0:
            print(f"\n[WARN] Warning: {len(result)} companies with negative equity:")
            for row in result:
                print(f"  - {row['ticker']}: {row['company_name']}")
                self.validation_results['warnings'].append(
                    f"Negative equity: {row['ticker']} ({row['company_name']})"
                )
        else:
            print("\n[OK] No negative equity cases found")

        # Check for unreasonably high ratios
        result = self.execute_query("""
            SELECT ticker, company_name, cost_of_revenue, total_revenue
            FROM financial_data
            WHERE fiscal_year = 2024
                AND cost_of_revenue IS NOT NULL
                AND total_revenue IS NOT NULL
                AND total_revenue > 0
                AND (cost_of_revenue / total_revenue) > 10
        """)

        if result and len(result) > 0:
            print(f"\n[WARN] Warning: {len(result)} companies with COGS > 10x Revenue:")
            for row in result:
                ratio = row['cost_of_revenue'] / row['total_revenue']
                print(f"  - {row['ticker']}: {row['company_name']} (ratio: {ratio:.1f}x)")
                self.validation_results['warnings'].append(
                    f"High COGS ratio: {row['ticker']} ({ratio:.1f}x)"
                )
        else:
            print("\n[OK] No anomalous revenue/cost ratios found")

    def check_sector_views(self):
        """Validate that sector-specific views exist and work"""
        print("\n" + "="*60)
        print("PHASE 5: Schema Validation (Views)")
        print("="*60)

        views_to_check = [
            'vw_banks_summary',
            'vw_industrial_summary',
            'vw_latest_financials'
        ]

        for view_name in views_to_check:
            try:
                result = self.execute_query(f"SELECT COUNT(*) as count FROM {view_name}")
                if result:
                    count = result[0]['count']
                    print(f"[OK] {view_name}: {count} records")
                    self.validation_results['passed'].append(f"View {view_name} exists")
            except Exception as e:
                print(f"[X] {view_name}: {e}")
                self.validation_results['failed'].append(f"View {view_name} error")

    def generate_report(self):
        """Generate final validation report"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)

        total_checks = (
            len(self.validation_results['passed']) +
            len(self.validation_results['failed']) +
            len(self.validation_results['warnings'])
        )

        print(f"\nTotal Checks: {total_checks}")
        print(f"[OK] Passed: {len(self.validation_results['passed'])}")
        print(f"[WARN] Warnings: {len(self.validation_results['warnings'])}")
        print(f"[X] Failed: {len(self.validation_results['failed'])}")

        if self.validation_results['failed']:
            print("\n[WARN] FAILED CHECKS:")
            for failure in self.validation_results['failed']:
                print(f"  - {failure}")

        if self.validation_results['warnings']:
            print("\n[WARN] WARNINGS:")
            for warning in self.validation_results['warnings']:
                print(f"  - {warning}")

        # Save report to file
        report_path = Path(__file__).parent.parent / 'data' / 'extracted' / 'VALIDATION_RESULTS.json'
        with open(report_path, 'w') as f:
            json.dump(self.validation_results, f, indent=2)

        print(f"\n[REPORT] Detailed results saved to: {report_path}")

        # Return status
        if len(self.validation_results['failed']) == 0:
            print("\n[SUCCESS] ALL VALIDATIONS PASSED")
            return True
        else:
            print("\n[FAILED] VALIDATION FAILED - Review errors above")
            return False


def main():
    """Main execution"""
    print("""
================================================================
     TASI Financial Data - Extraction Validation Script
                     Version 2.0.0
================================================================
    """)

    validator = DataValidator()

    if not validator.connect():
        print("\n[ERROR] Cannot proceed without database connection")
        sys.exit(1)

    try:
        # Run all validation phases
        validator.validate_record_counts()
        validator.validate_data_integrity()
        validator.validate_balance_sheet()
        validator.validate_data_quality()
        validator.check_sector_views()

        # Generate final report
        success = validator.generate_report()

        sys.exit(0 if success else 1)

    finally:
        validator.close()


if __name__ == "__main__":
    main()
