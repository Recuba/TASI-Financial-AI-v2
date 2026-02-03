"""
TASI Bank and Insurance Metrics Handler
========================================
This script handles financial metrics for banks and insurance companies
which report differently than traditional industrial/service companies.

Banks use:
- Net Interest Income (instead of Revenue)
- Net Interest Margin
- Cost-to-Income Ratio
- Loan-to-Deposit Ratio
- Non-Performing Loan Ratio
- Capital Adequacy Ratio

Insurance companies use:
- Gross Written Premiums (instead of Revenue)
- Net Earned Premiums
- Loss Ratio
- Combined Ratio
- Investment Income
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os

class InstitutionType(Enum):
    BANK = "bank"
    INSURANCE = "insurance"
    FINANCE = "finance"
    STANDARD = "standard"

@dataclass
class BankMetrics:
    """Bank-specific financial metrics"""
    ticker: int
    fiscal_year: int
    period_type: str
    net_interest_income: Optional[float] = None
    fee_income: Optional[float] = None
    trading_income: Optional[float] = None
    total_operating_income: Optional[float] = None
    operating_expenses: Optional[float] = None
    provisions: Optional[float] = None
    net_profit: Optional[float] = None
    total_assets: Optional[float] = None
    total_loans: Optional[float] = None
    total_deposits: Optional[float] = None
    total_equity: Optional[float] = None
    tier1_capital: Optional[float] = None
    risk_weighted_assets: Optional[float] = None
    non_performing_loans: Optional[float] = None

    # Calculated ratios
    net_interest_margin: Optional[float] = None
    cost_to_income_ratio: Optional[float] = None
    loan_to_deposit_ratio: Optional[float] = None
    npl_ratio: Optional[float] = None
    capital_adequacy_ratio: Optional[float] = None
    tier1_ratio: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None

@dataclass
class InsuranceMetrics:
    """Insurance company-specific financial metrics"""
    ticker: int
    fiscal_year: int
    period_type: str
    gross_written_premiums: Optional[float] = None
    net_written_premiums: Optional[float] = None
    net_earned_premiums: Optional[float] = None
    claims_incurred: Optional[float] = None
    policy_acquisition_costs: Optional[float] = None
    operating_expenses: Optional[float] = None
    investment_income: Optional[float] = None
    net_profit: Optional[float] = None
    total_assets: Optional[float] = None
    total_equity: Optional[float] = None
    technical_reserves: Optional[float] = None

    # Calculated ratios
    loss_ratio: Optional[float] = None
    expense_ratio: Optional[float] = None
    combined_ratio: Optional[float] = None
    retention_ratio: Optional[float] = None
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    solvency_ratio: Optional[float] = None

# TASI Bank and Insurance Company Classifications
BANK_TICKERS = {
    1010: "Riyad Bank",
    1020: "Bank Aljazira",
    1030: "Saudi Investment Bank",
    1050: "Banque Saudi Fransi",
    1060: "Saudi Awwal Bank",
    1080: "Arab National Bank",
    1120: "Al Rajhi Bank",
    1140: "Bank Albilad",
    1150: "Alinma Bank",
    1180: "The Saudi National Bank",
}

INSURANCE_TICKERS = {
    8010: "The Company for Cooperative Insurance",
    8012: "Aljazira Takaful Taawuni Co.",
    8020: "Malath Cooperative Insurance Co.",
    8030: "The Mediterranean and Gulf Insurance Co.",
    8040: "Allianz Saudi Fransi Cooperative Insurance",
    8050: "Salama Cooperative Insurance Co.",
    8060: "Walaa Cooperative Insurance Co.",
    8070: "Arabian Shield Cooperative Insurance",
    8100: "Saudi Arabian Cooperative Insurance",
    8120: "Gulf Union Cooperative Insurance Co.",
    8150: "Allied Cooperative Insurance Group",
    8160: "Arabia Insurance Cooperative Co.",
    8170: "Al-Etihad Cooperative Insurance Co.",
    8180: "Al Sagr Cooperative Insurance Co.",
    8190: "United Cooperative Assurance Co.",
    8200: "Saudi Re for Cooperative Reinsurance",
    8230: "Al-Rajhi Company for Cooperative Insurance",
    8240: "CHUBB Arabia Cooperative Insurance",
    8250: "AXA Cooperative Insurance Co.",
    8260: "Gulf General Cooperative Insurance",
    8280: "Al Alamiya for Cooperative Insurance",
    8300: "Wataniya Insurance Co.",
    8310: "Amana Cooperative Insurance Co.",
    8311: "Saudi Enaya Cooperative Insurance Co.",
}

FINANCE_COMPANY_TICKERS = {
    1182: "Amlak International Finance Co.",
    1183: "Saudi Home Loans Co.",
}


def get_institution_type(ticker: int) -> InstitutionType:
    """Determine the type of financial institution based on ticker"""
    if ticker in BANK_TICKERS:
        return InstitutionType.BANK
    elif ticker in INSURANCE_TICKERS:
        return InstitutionType.INSURANCE
    elif ticker in FINANCE_COMPANY_TICKERS:
        return InstitutionType.FINANCE
    else:
        return InstitutionType.STANDARD


def calculate_bank_ratios(metrics: BankMetrics) -> BankMetrics:
    """
    Calculate bank-specific ratios from raw metrics
    """
    # Net Interest Margin = Net Interest Income / Average Interest-Earning Assets
    if metrics.net_interest_income and metrics.total_assets:
        # Approximation: using total assets as proxy for interest-earning assets
        metrics.net_interest_margin = (metrics.net_interest_income / metrics.total_assets) * 100

    # Cost-to-Income Ratio = Operating Expenses / Total Operating Income
    if metrics.operating_expenses and metrics.total_operating_income and metrics.total_operating_income != 0:
        metrics.cost_to_income_ratio = (metrics.operating_expenses / metrics.total_operating_income) * 100

    # Loan-to-Deposit Ratio = Total Loans / Total Deposits
    if metrics.total_loans and metrics.total_deposits and metrics.total_deposits != 0:
        metrics.loan_to_deposit_ratio = (metrics.total_loans / metrics.total_deposits) * 100

    # NPL Ratio = Non-Performing Loans / Total Loans
    if metrics.non_performing_loans is not None and metrics.total_loans and metrics.total_loans != 0:
        metrics.npl_ratio = (metrics.non_performing_loans / metrics.total_loans) * 100

    # Capital Adequacy Ratio = (Tier 1 + Tier 2 Capital) / Risk-Weighted Assets
    if metrics.tier1_capital and metrics.risk_weighted_assets and metrics.risk_weighted_assets != 0:
        metrics.capital_adequacy_ratio = (metrics.tier1_capital / metrics.risk_weighted_assets) * 100
        metrics.tier1_ratio = metrics.capital_adequacy_ratio  # Simplified

    # Return on Equity = Net Profit / Total Equity
    if metrics.net_profit and metrics.total_equity and metrics.total_equity != 0:
        metrics.return_on_equity = (metrics.net_profit / metrics.total_equity) * 100

    # Return on Assets = Net Profit / Total Assets
    if metrics.net_profit and metrics.total_assets and metrics.total_assets != 0:
        metrics.return_on_assets = (metrics.net_profit / metrics.total_assets) * 100

    return metrics


def calculate_insurance_ratios(metrics: InsuranceMetrics) -> InsuranceMetrics:
    """
    Calculate insurance-specific ratios from raw metrics
    """
    # Loss Ratio = Claims Incurred / Net Earned Premiums
    if metrics.claims_incurred and metrics.net_earned_premiums and metrics.net_earned_premiums != 0:
        metrics.loss_ratio = (metrics.claims_incurred / metrics.net_earned_premiums) * 100

    # Expense Ratio = (Acquisition Costs + Operating Expenses) / Net Earned Premiums
    if metrics.net_earned_premiums and metrics.net_earned_premiums != 0:
        total_expenses = (metrics.policy_acquisition_costs or 0) + (metrics.operating_expenses or 0)
        metrics.expense_ratio = (total_expenses / metrics.net_earned_premiums) * 100

    # Combined Ratio = Loss Ratio + Expense Ratio
    if metrics.loss_ratio is not None and metrics.expense_ratio is not None:
        metrics.combined_ratio = metrics.loss_ratio + metrics.expense_ratio

    # Retention Ratio = Net Written Premiums / Gross Written Premiums
    if metrics.net_written_premiums and metrics.gross_written_premiums and metrics.gross_written_premiums != 0:
        metrics.retention_ratio = (metrics.net_written_premiums / metrics.gross_written_premiums) * 100

    # Return on Equity
    if metrics.net_profit and metrics.total_equity and metrics.total_equity != 0:
        metrics.return_on_equity = (metrics.net_profit / metrics.total_equity) * 100

    # Return on Assets
    if metrics.net_profit and metrics.total_assets and metrics.total_assets != 0:
        metrics.return_on_assets = (metrics.net_profit / metrics.total_assets) * 100

    # Solvency Ratio = Total Equity / Technical Reserves (simplified)
    if metrics.total_equity and metrics.technical_reserves and metrics.technical_reserves != 0:
        metrics.solvency_ratio = (metrics.total_equity / metrics.technical_reserves) * 100

    return metrics


def process_bank_data(df: pd.DataFrame, ticker: int) -> List[BankMetrics]:
    """
    Process raw financial data for a bank and calculate bank-specific metrics

    For banks, we need to map standard columns differently:
    - net_profit -> remains as net_profit
    - Revenue is typically NULL for banks; use net_interest_income if available
    - total_assets -> total_assets
    - total_equity -> total_equity
    """
    bank_data = df[df['ticker'] == ticker].copy()
    results = []

    for _, row in bank_data.iterrows():
        metrics = BankMetrics(
            ticker=int(row['ticker']),
            fiscal_year=int(row['fiscal_year']) if pd.notna(row['fiscal_year']) else None,
            period_type=row['period_type'],
            net_profit=row['net_profit'] if pd.notna(row['net_profit']) else None,
            total_assets=row['total_assets'] if pd.notna(row['total_assets']) else None,
            total_equity=row['total_equity'] if pd.notna(row['total_equity']) else None,
        )

        # Calculate ratios based on available data
        metrics = calculate_bank_ratios(metrics)
        results.append(metrics)

    return results


def process_insurance_data(df: pd.DataFrame, ticker: int) -> List[InsuranceMetrics]:
    """
    Process raw financial data for an insurance company

    For insurance companies:
    - Revenue is typically NULL; use gross_written_premiums if available
    - net_profit -> remains as net_profit
    """
    insurance_data = df[df['ticker'] == ticker].copy()
    results = []

    for _, row in insurance_data.iterrows():
        metrics = InsuranceMetrics(
            ticker=int(row['ticker']),
            fiscal_year=int(row['fiscal_year']) if pd.notna(row['fiscal_year']) else None,
            period_type=row['period_type'],
            net_profit=row['net_profit'] if pd.notna(row['net_profit']) else None,
            total_assets=row['total_assets'] if pd.notna(row['total_assets']) else None,
            total_equity=row['total_equity'] if pd.notna(row['total_equity']) else None,
        )

        # Calculate ratios based on available data
        metrics = calculate_insurance_ratios(metrics)
        results.append(metrics)

    return results


def create_unified_metrics_df(
    bank_metrics: List[BankMetrics],
    insurance_metrics: List[InsuranceMetrics]
) -> pd.DataFrame:
    """
    Create a unified DataFrame with metrics for all financial institutions
    """
    records = []

    # Process bank metrics
    for m in bank_metrics:
        records.append({
            'ticker': m.ticker,
            'company_name': BANK_TICKERS.get(m.ticker, 'Unknown'),
            'institution_type': 'BANK',
            'fiscal_year': m.fiscal_year,
            'period_type': m.period_type,
            'primary_income': m.net_interest_income or m.total_operating_income,
            'primary_income_metric': 'Net Interest Income',
            'net_profit': m.net_profit,
            'total_assets': m.total_assets,
            'total_equity': m.total_equity,
            'roe_pct': m.return_on_equity,
            'roa_pct': m.return_on_assets,
            'key_ratio_1_name': 'Net Interest Margin',
            'key_ratio_1_value': m.net_interest_margin,
            'key_ratio_2_name': 'Cost-to-Income Ratio',
            'key_ratio_2_value': m.cost_to_income_ratio,
            'key_ratio_3_name': 'Loan-to-Deposit Ratio',
            'key_ratio_3_value': m.loan_to_deposit_ratio,
            'key_ratio_4_name': 'NPL Ratio',
            'key_ratio_4_value': m.npl_ratio,
            'key_ratio_5_name': 'Capital Adequacy Ratio',
            'key_ratio_5_value': m.capital_adequacy_ratio,
        })

    # Process insurance metrics
    for m in insurance_metrics:
        records.append({
            'ticker': m.ticker,
            'company_name': INSURANCE_TICKERS.get(m.ticker, 'Unknown'),
            'institution_type': 'INSURANCE',
            'fiscal_year': m.fiscal_year,
            'period_type': m.period_type,
            'primary_income': m.gross_written_premiums or m.net_earned_premiums,
            'primary_income_metric': 'Gross Written Premiums',
            'net_profit': m.net_profit,
            'total_assets': m.total_assets,
            'total_equity': m.total_equity,
            'roe_pct': m.return_on_equity,
            'roa_pct': m.return_on_assets,
            'key_ratio_1_name': 'Loss Ratio',
            'key_ratio_1_value': m.loss_ratio,
            'key_ratio_2_name': 'Combined Ratio',
            'key_ratio_2_value': m.combined_ratio,
            'key_ratio_3_name': 'Expense Ratio',
            'key_ratio_3_value': m.expense_ratio,
            'key_ratio_4_name': 'Retention Ratio',
            'key_ratio_4_value': m.retention_ratio,
            'key_ratio_5_name': 'Solvency Ratio',
            'key_ratio_5_value': m.solvency_ratio,
        })

    return pd.DataFrame(records)


def update_database_with_corrected_metrics(
    df: pd.DataFrame,
    output_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Main function to process the TASI database and add corrected metrics
    for banks and insurance companies.

    Args:
        df: The original TASI financials DataFrame
        output_path: Optional path to save the updated DataFrame

    Returns:
        Updated DataFrame with corrected metrics for financial institutions
    """
    # Add institution type column
    df['institution_type'] = df['ticker'].apply(
        lambda x: get_institution_type(int(x) if pd.notna(x) else 0).value
    )

    # Add primary income metric name
    df['primary_income_metric'] = df['institution_type'].map({
        'bank': 'Net Interest Income',
        'insurance': 'Gross Written Premiums',
        'finance': 'Interest Income',
        'standard': 'Revenue'
    })

    # For banks, calculate ROE and ROA from net_profit where revenue is null
    bank_mask = df['institution_type'] == 'bank'

    # Calculate ROE for banks (if not already calculated)
    df.loc[bank_mask & df['return_on_equity'].isna(), 'calc_ROE'] = (
        df.loc[bank_mask & df['return_on_equity'].isna()].apply(
            lambda row: (row['net_profit'] / row['total_equity'] * 100)
            if pd.notna(row['net_profit']) and pd.notna(row['total_equity']) and row['total_equity'] != 0
            else None,
            axis=1
        )
    )

    # Calculate ROA for banks
    df.loc[bank_mask & df['return_on_assets'].isna(), 'calc_ROA'] = (
        df.loc[bank_mask & df['return_on_assets'].isna()].apply(
            lambda row: (row['net_profit'] / row['total_assets'] * 100)
            if pd.notna(row['net_profit']) and pd.notna(row['total_assets']) and row['total_assets'] != 0
            else None,
            axis=1
        )
    )

    # Same for insurance companies
    insurance_mask = df['institution_type'] == 'insurance'

    df.loc[insurance_mask & df['return_on_equity'].isna(), 'calc_ROE'] = (
        df.loc[insurance_mask & df['return_on_equity'].isna()].apply(
            lambda row: (row['net_profit'] / row['total_equity'] * 100)
            if pd.notna(row['net_profit']) and pd.notna(row['total_equity']) and row['total_equity'] != 0
            else None,
            axis=1
        )
    )

    df.loc[insurance_mask & df['return_on_assets'].isna(), 'calc_ROA'] = (
        df.loc[insurance_mask & df['return_on_assets'].isna()].apply(
            lambda row: (row['net_profit'] / row['total_assets'] * 100)
            if pd.notna(row['net_profit']) and pd.notna(row['total_assets']) and row['total_assets'] != 0
            else None,
            axis=1
        )
    )

    # Add flag for companies requiring special metric sourcing
    df['requires_special_metrics'] = df['institution_type'].isin(['bank', 'insurance', 'finance'])

    # Add notes for revenue interpretation
    df['revenue_note'] = df['institution_type'].map({
        'bank': 'Banks: Use Net Interest Income instead of Revenue',
        'insurance': 'Insurance: Use Gross Written Premiums instead of Revenue',
        'finance': 'Finance Co: Use Interest/Fee Income instead of Revenue',
        'standard': None
    })

    if output_path:
        df.to_csv(output_path, index=False)
        print(f"Updated database saved to: {output_path}")

    return df


def generate_financial_institution_report(df: pd.DataFrame) -> str:
    """
    Generate a summary report of financial institutions in the database
    """
    report = []
    report.append("=" * 70)
    report.append("TASI Financial Institutions Summary Report")
    report.append("=" * 70)

    # Banks summary
    banks = df[df['institution_type'] == 'bank']
    report.append(f"\nBANKS ({len(BANK_TICKERS)} total)")
    report.append("-" * 40)
    for ticker, name in sorted(BANK_TICKERS.items()):
        bank_data = banks[banks['ticker'] == ticker]
        years = sorted(bank_data['fiscal_year'].dropna().unique())
        year_range = f"{int(min(years))}-{int(max(years))}" if years else "No data"
        report.append(f"  {ticker}: {name} [{year_range}]")

    # Insurance summary
    insurance = df[df['institution_type'] == 'insurance']
    report.append(f"\nINSURANCE COMPANIES ({len(INSURANCE_TICKERS)} total)")
    report.append("-" * 40)
    for ticker, name in sorted(INSURANCE_TICKERS.items()):
        ins_data = insurance[insurance['ticker'] == ticker]
        years = sorted(ins_data['fiscal_year'].dropna().unique())
        year_range = f"{int(min(years))}-{int(max(years))}" if years else "No data"
        report.append(f"  {ticker}: {name} [{year_range}]")

    # Metrics guidance
    report.append("\n" + "=" * 70)
    report.append("METRICS GUIDANCE")
    report.append("=" * 70)

    report.append("\nFor BANKS, use these metrics instead of standard ratios:")
    report.append("  - Revenue -> Net Interest Income + Fee Income + Trading Income")
    report.append("  - Gross Margin -> Net Interest Margin")
    report.append("  - Operating Margin -> Cost-to-Income Ratio (inverse)")
    report.append("  - Debt Ratio -> Loan-to-Deposit Ratio")
    report.append("  - Asset Quality -> NPL Ratio")
    report.append("  - Solvency -> Capital Adequacy Ratio (CAR)")

    report.append("\nFor INSURANCE COMPANIES, use these metrics instead:")
    report.append("  - Revenue -> Gross Written Premiums")
    report.append("  - Gross Margin -> Retention Ratio")
    report.append("  - Operating Margin -> Combined Ratio (inverse - lower is better)")
    report.append("  - Loss Performance -> Loss Ratio")
    report.append("  - Solvency -> Solvency Margin Ratio")

    return "\n".join(report)


# Main execution
if __name__ == "__main__":
    # Path to the TASI database
    DB_PATH = r"C:\Users\User\venna-ai\TASI_financials_DB.csv"
    OUTPUT_PATH = r"C:\Users\User\venna-ai\TASI_financials_DB_corrected.csv"

    print("Loading TASI Financial Database...")

    if os.path.exists(DB_PATH):
        df = pd.read_csv(DB_PATH)
        print(f"Loaded {len(df)} records")

        # Update with corrected metrics
        print("\nProcessing financial institution metrics...")
        df_updated = update_database_with_corrected_metrics(df, OUTPUT_PATH)

        # Generate report
        print("\n" + generate_financial_institution_report(df_updated))

        # Summary statistics
        print("\n" + "=" * 70)
        print("SUMMARY STATISTICS")
        print("=" * 70)
        print(f"\nTotal records: {len(df_updated)}")
        print(f"Banks: {len(df_updated[df_updated['institution_type'] == 'bank'])}")
        print(f"Insurance: {len(df_updated[df_updated['institution_type'] == 'insurance'])}")
        print(f"Finance: {len(df_updated[df_updated['institution_type'] == 'finance'])}")
        print(f"Standard companies: {len(df_updated[df_updated['institution_type'] == 'standard'])}")

        print(f"\nUpdated database saved to: {OUTPUT_PATH}")
    else:
        print(f"Database file not found: {DB_PATH}")
        print("Please ensure the file exists and try again.")
