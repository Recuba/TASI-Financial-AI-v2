-- =============================================================================
-- TASI Financial Database - 2024 Data Update Script
-- Adds support for Banks, Insurance, and Industrial companies with
-- sector-specific financial metrics
-- =============================================================================

-- =============================================================================
-- 1. COMPANY TYPE MAPPING TABLE
-- =============================================================================

-- Create company type mapping table
CREATE TABLE IF NOT EXISTS company_types (
    company_type_id SERIAL PRIMARY KEY,
    type_code VARCHAR(20) UNIQUE NOT NULL,
    type_name VARCHAR(100) NOT NULL,
    type_description TEXT,
    revenue_metric_name VARCHAR(100),  -- What to use instead of "revenue"
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE company_types IS 'Company type classifications (BANK, INSURANCE, FINANCE, STANDARD) with specific metric requirements';
COMMENT ON COLUMN company_types.revenue_metric_name IS 'The primary income metric for this company type (e.g., Net Interest Income for banks, Gross Written Premiums for insurance)';

-- Insert company types
INSERT INTO company_types (type_code, type_name, type_description, revenue_metric_name) VALUES
('BANK', 'Commercial Bank', 'Commercial and retail banks - use Net Interest Income instead of Revenue', 'Net Interest Income'),
('INSURANCE', 'Insurance Company', 'Insurance and reinsurance companies - use Gross Written Premiums instead of Revenue', 'Gross Written Premiums'),
('FINANCE', 'Finance Company', 'Non-bank financial institutions - mortgage, consumer finance', 'Interest Income'),
('STANDARD', 'Standard Company', 'Industrial, service, and other non-financial companies', 'Revenue')
ON CONFLICT (type_code) DO UPDATE
SET type_name = EXCLUDED.type_name,
    type_description = EXCLUDED.type_description,
    revenue_metric_name = EXCLUDED.revenue_metric_name;

-- =============================================================================
-- 2. SECTOR MAPPING TABLE (Links tickers to company types and sectors)
-- =============================================================================

CREATE TABLE IF NOT EXISTS company_sector_mapping (
    mapping_id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_type_id INTEGER REFERENCES company_types(company_type_id),
    gics_sector_code VARCHAR(20),
    sub_type VARCHAR(50),  -- e.g., "Islamic Bank", "Multi-line Insurance"
    regulator VARCHAR(50),  -- e.g., "SAMA", "Insurance Authority"
    market_cap_rank VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE company_sector_mapping IS 'Maps tickers to company types and regulatory information';
COMMENT ON COLUMN company_sector_mapping.sub_type IS 'More specific type: Islamic Bank, Multi-line Insurance, etc.';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_csm_ticker ON company_sector_mapping(ticker);
CREATE INDEX IF NOT EXISTS idx_csm_type ON company_sector_mapping(company_type_id);

-- Insert bank mappings
INSERT INTO company_sector_mapping (ticker, company_type_id, sub_type, regulator)
SELECT ticker::VARCHAR,
       (SELECT company_type_id FROM company_types WHERE type_code = 'BANK'),
       CASE
           WHEN ticker::INTEGER IN (1020, 1120, 1140, 1150) THEN 'Islamic Bank'
           ELSE 'Commercial Bank'
       END,
       'SAMA'
FROM (VALUES
    (1010), (1020), (1030), (1050), (1060),
    (1080), (1120), (1140), (1150), (1180)
) AS banks(ticker)
ON CONFLICT (ticker) DO UPDATE
SET company_type_id = EXCLUDED.company_type_id,
    sub_type = EXCLUDED.sub_type,
    regulator = EXCLUDED.regulator;

-- Insert insurance mappings
INSERT INTO company_sector_mapping (ticker, company_type_id, sub_type, regulator)
SELECT ticker::VARCHAR,
       (SELECT company_type_id FROM company_types WHERE type_code = 'INSURANCE'),
       CASE
           WHEN ticker::INTEGER IN (8012, 8050, 8230) THEN 'Takaful (Islamic Insurance)'
           WHEN ticker::INTEGER = 8200 THEN 'Reinsurance'
           WHEN ticker::INTEGER = 8311 THEN 'Health Insurance'
           ELSE 'Multi-line Insurance'
       END,
       'Insurance Authority'
FROM (VALUES
    (8010), (8012), (8020), (8030), (8040), (8050), (8060), (8070),
    (8100), (8120), (8150), (8160), (8170), (8180), (8190), (8200),
    (8230), (8240), (8250), (8260), (8280), (8300), (8310), (8311)
) AS insurance(ticker)
ON CONFLICT (ticker) DO UPDATE
SET company_type_id = EXCLUDED.company_type_id,
    sub_type = EXCLUDED.sub_type,
    regulator = EXCLUDED.regulator;

-- Insert finance company mappings
INSERT INTO company_sector_mapping (ticker, company_type_id, sub_type, regulator)
SELECT ticker::VARCHAR,
       (SELECT company_type_id FROM company_types WHERE type_code = 'FINANCE'),
       CASE
           WHEN ticker::INTEGER = 1182 THEN 'Real Estate Finance'
           WHEN ticker::INTEGER = 1183 THEN 'Mortgage Finance'
           ELSE 'Finance Company'
       END,
       'SAMA'
FROM (VALUES (1182), (1183)) AS finance(ticker)
ON CONFLICT (ticker) DO UPDATE
SET company_type_id = EXCLUDED.company_type_id,
    sub_type = EXCLUDED.sub_type,
    regulator = EXCLUDED.regulator;

-- =============================================================================
-- 3. ADD SECTOR-SPECIFIC COLUMNS TO FINANCIAL_STATEMENTS
-- =============================================================================

-- Bank-specific metrics
ALTER TABLE financial_statements
ADD COLUMN IF NOT EXISTS net_interest_income NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS fee_income NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS trading_income NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS total_operating_income NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS provisions NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS total_loans NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS total_deposits NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS tier1_capital NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS risk_weighted_assets NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS non_performing_loans NUMERIC(20,2);

-- Insurance-specific metrics
ALTER TABLE financial_statements
ADD COLUMN IF NOT EXISTS gross_written_premiums NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS net_written_premiums NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS net_earned_premiums NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS claims_incurred NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS policy_acquisition_costs NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS investment_income NUMERIC(20,2),
ADD COLUMN IF NOT EXISTS technical_reserves NUMERIC(20,2);

-- Add comments
COMMENT ON COLUMN financial_statements.net_interest_income IS 'Bank metric: Net interest income (interest received - interest paid) in SAR';
COMMENT ON COLUMN financial_statements.fee_income IS 'Bank/Finance metric: Fee and commission income in SAR';
COMMENT ON COLUMN financial_statements.gross_written_premiums IS 'Insurance metric: Total premiums written before reinsurance in SAR';
COMMENT ON COLUMN financial_statements.claims_incurred IS 'Insurance metric: Total claims paid and reserved in SAR';

-- =============================================================================
-- 4. ADD SECTOR-SPECIFIC RATIOS TO FINANCIAL_METRICS
-- =============================================================================

ALTER TABLE financial_metrics
ADD COLUMN IF NOT EXISTS net_interest_margin NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS cost_to_income_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS loan_to_deposit_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS npl_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS capital_adequacy_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS tier1_ratio NUMERIC(10,6);

-- Insurance ratios
ALTER TABLE financial_metrics
ADD COLUMN IF NOT EXISTS loss_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS expense_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS combined_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS retention_ratio NUMERIC(10,6),
ADD COLUMN IF NOT EXISTS solvency_ratio NUMERIC(10,6);

-- Add comments
COMMENT ON COLUMN financial_metrics.net_interest_margin IS 'Bank metric: Net Interest Income / Average Earning Assets as decimal';
COMMENT ON COLUMN financial_metrics.cost_to_income_ratio IS 'Bank metric: Operating Expenses / Operating Income as decimal';
COMMENT ON COLUMN financial_metrics.npl_ratio IS 'Bank metric: Non-Performing Loans / Total Loans as decimal';
COMMENT ON COLUMN financial_metrics.loss_ratio IS 'Insurance metric: Claims Incurred / Net Earned Premiums as decimal';
COMMENT ON COLUMN financial_metrics.combined_ratio IS 'Insurance metric: (Loss Ratio + Expense Ratio) - lower is better';

-- =============================================================================
-- 5. CREATE SECTOR-SPECIFIC VIEWS
-- =============================================================================

-- View: Latest Bank Financial Data
DROP VIEW IF EXISTS v_banks_latest CASCADE;
CREATE VIEW v_banks_latest AS
SELECT
    c.ticker,
    c.company_name,
    csm.sub_type AS bank_type,
    fp.fiscal_year,
    fp.fiscal_quarter,
    fp.period_label,

    -- Bank Income Statement (in millions)
    ROUND(fs.net_interest_income / 1000000, 2) AS net_interest_income_m,
    ROUND(fs.fee_income / 1000000, 2) AS fee_income_m,
    ROUND(fs.trading_income / 1000000, 2) AS trading_income_m,
    ROUND(fs.total_operating_income / 1000000, 2) AS total_operating_income_m,
    ROUND(fs.net_profit / 1000000, 2) AS net_profit_m,
    ROUND(fs.provisions / 1000000, 2) AS provisions_m,

    -- Bank Balance Sheet (in millions)
    ROUND(fs.total_assets / 1000000, 2) AS total_assets_m,
    ROUND(fs.total_equity / 1000000, 2) AS total_equity_m,
    ROUND(fs.total_loans / 1000000, 2) AS total_loans_m,
    ROUND(fs.total_deposits / 1000000, 2) AS total_deposits_m,
    ROUND(fs.tier1_capital / 1000000, 2) AS tier1_capital_m,
    ROUND(fs.non_performing_loans / 1000000, 2) AS npl_m,

    -- Bank Ratios (as percentages)
    ROUND(fm.net_interest_margin * 100, 2) AS nim_percent,
    ROUND(fm.cost_to_income_ratio * 100, 2) AS cost_to_income_percent,
    ROUND(fm.loan_to_deposit_ratio * 100, 2) AS loan_to_deposit_percent,
    ROUND(fm.npl_ratio * 100, 2) AS npl_percent,
    ROUND(fm.capital_adequacy_ratio * 100, 2) AS capital_adequacy_percent,
    ROUND(fm.tier1_ratio * 100, 2) AS tier1_percent,
    ROUND(fm.return_on_equity * 100, 2) AS roe_percent,
    ROUND(fm.return_on_assets * 100, 2) AS roa_percent,

    -- Flags
    fs.is_latest,
    fp.period_type = 'Annual' AS is_annual,
    fs.data_quality_score
FROM financial_statements fs
JOIN companies c ON fs.company_id = c.company_id
JOIN fiscal_periods fp ON fs.period_id = fp.period_id
JOIN company_sector_mapping csm ON c.ticker = csm.ticker
LEFT JOIN financial_metrics fm ON fs.statement_id = fm.statement_id
WHERE csm.company_type_id = (SELECT company_type_id FROM company_types WHERE type_code = 'BANK');

COMMENT ON VIEW v_banks_latest IS 'Bank financial data with bank-specific metrics (NII, NIM, loan/deposit ratios, NPL)';

-- View: Latest Insurance Company Financial Data
DROP VIEW IF EXISTS v_insurance_latest CASCADE;
CREATE VIEW v_insurance_latest AS
SELECT
    c.ticker,
    c.company_name,
    csm.sub_type AS insurance_type,
    fp.fiscal_year,
    fp.fiscal_quarter,
    fp.period_label,

    -- Insurance Income Statement (in millions)
    ROUND(fs.gross_written_premiums / 1000000, 2) AS gross_written_premiums_m,
    ROUND(fs.net_written_premiums / 1000000, 2) AS net_written_premiums_m,
    ROUND(fs.net_earned_premiums / 1000000, 2) AS net_earned_premiums_m,
    ROUND(fs.claims_incurred / 1000000, 2) AS claims_incurred_m,
    ROUND(fs.policy_acquisition_costs / 1000000, 2) AS acquisition_costs_m,
    ROUND(fs.investment_income / 1000000, 2) AS investment_income_m,
    ROUND(fs.net_profit / 1000000, 2) AS net_profit_m,

    -- Insurance Balance Sheet (in millions)
    ROUND(fs.total_assets / 1000000, 2) AS total_assets_m,
    ROUND(fs.total_equity / 1000000, 2) AS total_equity_m,
    ROUND(fs.technical_reserves / 1000000, 2) AS technical_reserves_m,

    -- Insurance Ratios (as percentages)
    ROUND(fm.loss_ratio * 100, 2) AS loss_ratio_percent,
    ROUND(fm.expense_ratio * 100, 2) AS expense_ratio_percent,
    ROUND(fm.combined_ratio * 100, 2) AS combined_ratio_percent,
    ROUND(fm.retention_ratio * 100, 2) AS retention_ratio_percent,
    ROUND(fm.solvency_ratio * 100, 2) AS solvency_ratio_percent,
    ROUND(fm.return_on_equity * 100, 2) AS roe_percent,
    ROUND(fm.return_on_assets * 100, 2) AS roa_percent,

    -- Flags
    fs.is_latest,
    fp.period_type = 'Annual' AS is_annual,
    fs.data_quality_score
FROM financial_statements fs
JOIN companies c ON fs.company_id = c.company_id
JOIN fiscal_periods fp ON fs.period_id = fp.period_id
JOIN company_sector_mapping csm ON c.ticker = csm.ticker
LEFT JOIN financial_metrics fm ON fs.statement_id = fm.statement_id
WHERE csm.company_type_id = (SELECT company_type_id FROM company_types WHERE type_code = 'INSURANCE');

COMMENT ON VIEW v_insurance_latest IS 'Insurance company financial data with insurance-specific metrics (GWP, claims, combined ratio)';

-- View: Latest Industrial/Standard Company Financial Data
DROP VIEW IF EXISTS v_industrial_latest CASCADE;
CREATE VIEW v_industrial_latest AS
SELECT
    c.ticker,
    c.company_name,
    c.company_type,
    s.sector_name AS sector,
    fp.fiscal_year,
    fp.fiscal_quarter,
    fp.period_label,

    -- Income Statement (in millions)
    ROUND(fs.revenue / 1000000, 2) AS revenue_m,
    ROUND(fs.cost_of_sales / 1000000, 2) AS cogs_m,
    ROUND(fs.gross_profit / 1000000, 2) AS gross_profit_m,
    ROUND(fs.operating_profit / 1000000, 2) AS operating_profit_m,
    ROUND(fs.net_profit / 1000000, 2) AS net_profit_m,

    -- Balance Sheet (in millions)
    ROUND(fs.total_assets / 1000000, 2) AS total_assets_m,
    ROUND(fs.total_equity / 1000000, 2) AS total_equity_m,
    ROUND(fs.total_liabilities / 1000000, 2) AS total_liabilities_m,

    -- Ratios (as percentages)
    ROUND(fm.gross_margin * 100, 2) AS gross_margin_percent,
    ROUND(fm.operating_margin * 100, 2) AS operating_margin_percent,
    ROUND(fm.net_margin * 100, 2) AS net_margin_percent,
    ROUND(fm.return_on_equity * 100, 2) AS roe_percent,
    ROUND(fm.return_on_assets * 100, 2) AS roa_percent,
    ROUND(fm.debt_to_equity * 100, 2) AS debt_to_equity_percent,

    -- Flags
    fs.is_latest,
    fp.period_type = 'Annual' AS is_annual,
    fs.data_quality_score
FROM financial_statements fs
JOIN companies c ON fs.company_id = c.company_id
JOIN fiscal_periods fp ON fs.period_id = fp.period_id
LEFT JOIN sectors s ON c.sector_id = s.sector_id
LEFT JOIN financial_metrics fm ON fs.statement_id = fm.statement_id
LEFT JOIN company_sector_mapping csm ON c.ticker = csm.ticker
WHERE csm.company_type_id IS NULL
   OR csm.company_type_id = (SELECT company_type_id FROM company_types WHERE type_code = 'STANDARD');

COMMENT ON VIEW v_industrial_latest IS 'Standard industrial and service company financial data';

-- View: All Companies with 2024 Data (unified view across all types)
DROP VIEW IF EXISTS v_all_companies_2024 CASCADE;
CREATE VIEW v_all_companies_2024 AS
SELECT
    c.ticker,
    c.company_name,
    COALESCE(ct.type_name, 'Standard') AS company_type,
    csm.sub_type,
    s.sector_name AS sector,
    fp.fiscal_year,
    fp.fiscal_quarter,
    fp.period_label,
    fp.period_type,

    -- Primary income metric (varies by company type)
    CASE
        WHEN ct.type_code = 'BANK' THEN fs.net_interest_income
        WHEN ct.type_code = 'INSURANCE' THEN fs.gross_written_premiums
        WHEN ct.type_code = 'FINANCE' THEN COALESCE(fs.net_interest_income, fs.revenue)
        ELSE fs.revenue
    END / 1000000.0 AS primary_income_m,

    CASE
        WHEN ct.type_code = 'BANK' THEN 'Net Interest Income'
        WHEN ct.type_code = 'INSURANCE' THEN 'Gross Written Premiums'
        WHEN ct.type_code = 'FINANCE' THEN 'Interest Income'
        ELSE 'Revenue'
    END AS income_metric_name,

    -- Common metrics
    ROUND(fs.net_profit / 1000000, 2) AS net_profit_m,
    ROUND(fs.total_assets / 1000000, 2) AS total_assets_m,
    ROUND(fs.total_equity / 1000000, 2) AS total_equity_m,

    -- Profitability
    ROUND(fm.return_on_equity * 100, 2) AS roe_percent,
    ROUND(fm.return_on_assets * 100, 2) AS roa_percent,

    -- Status
    fm.profit_status,
    fm.roe_status,

    -- Flags
    fs.is_latest,
    fp.period_type = 'Annual' AS is_annual,
    fs.data_quality_score
FROM financial_statements fs
JOIN companies c ON fs.company_id = c.company_id
JOIN fiscal_periods fp ON fs.period_id = fp.period_id
LEFT JOIN sectors s ON c.sector_id = s.sector_id
LEFT JOIN company_sector_mapping csm ON c.ticker = csm.ticker
LEFT JOIN company_types ct ON csm.company_type_id = ct.company_type_id
LEFT JOIN financial_metrics fm ON fs.statement_id = fm.statement_id
WHERE fp.fiscal_year = 2024;

COMMENT ON VIEW v_all_companies_2024 IS 'All companies with 2024 data showing appropriate income metric per company type';

-- =============================================================================
-- 6. UPDATE MATERIALIZED VIEW
-- =============================================================================

-- Drop and recreate the materialized view with company type information
DROP MATERIALIZED VIEW IF EXISTS company_financials CASCADE;

CREATE MATERIALIZED VIEW company_financials AS
SELECT
    -- Company Info
    c.ticker,
    c.company_name,
    c.company_type,
    c.size_category,
    s.sector_name AS sector,
    COALESCE(ct.type_name, 'Standard') AS institution_type,
    csm.sub_type AS institution_subtype,

    -- Period Info
    fp.fiscal_year,
    fp.fiscal_quarter,
    fp.period_type,
    fp.period_end,
    fp.period_label,

    -- Primary Income Metric (varies by institution type)
    CASE
        WHEN ct.type_code = 'BANK' THEN ROUND(fs.net_interest_income / 1000000, 2)
        WHEN ct.type_code = 'INSURANCE' THEN ROUND(fs.gross_written_premiums / 1000000, 2)
        WHEN ct.type_code = 'FINANCE' THEN ROUND(COALESCE(fs.net_interest_income, fs.revenue) / 1000000, 2)
        ELSE ROUND(fs.revenue / 1000000, 2)
    END AS primary_income_millions,

    CASE
        WHEN ct.type_code = 'BANK' THEN 'Net Interest Income'
        WHEN ct.type_code = 'INSURANCE' THEN 'Gross Written Premiums'
        WHEN ct.type_code = 'FINANCE' THEN 'Interest Income'
        ELSE 'Revenue'
    END AS income_metric_label,

    -- Standard Income Statement (in millions)
    ROUND(fs.revenue / 1000000, 2) AS revenue_millions,
    ROUND(fs.cost_of_sales / 1000000, 2) AS cogs_millions,
    ROUND(fs.gross_profit / 1000000, 2) AS gross_profit_millions,
    ROUND(fs.operating_profit / 1000000, 2) AS operating_profit_millions,
    ROUND(fs.net_profit / 1000000, 2) AS net_profit_millions,

    -- Balance Sheet (in millions)
    ROUND(fs.total_assets / 1000000, 2) AS total_assets_millions,
    ROUND(fs.total_equity / 1000000, 2) AS total_equity_millions,
    ROUND(fs.total_liabilities / 1000000, 2) AS total_liabilities_millions,

    -- Cash Flow (in millions)
    ROUND(fs.operating_cash_flow / 1000000, 2) AS operating_cash_flow_millions,
    ROUND(fs.free_cash_flow / 1000000, 2) AS free_cash_flow_millions,

    -- Bank-specific metrics (in millions)
    ROUND(fs.net_interest_income / 1000000, 2) AS net_interest_income_millions,
    ROUND(fs.fee_income / 1000000, 2) AS fee_income_millions,
    ROUND(fs.total_loans / 1000000, 2) AS total_loans_millions,
    ROUND(fs.total_deposits / 1000000, 2) AS total_deposits_millions,

    -- Insurance-specific metrics (in millions)
    ROUND(fs.gross_written_premiums / 1000000, 2) AS gross_written_premiums_millions,
    ROUND(fs.claims_incurred / 1000000, 2) AS claims_incurred_millions,

    -- Key Ratios (as percentages)
    ROUND(fm.return_on_equity * 100, 2) AS roe_percent,
    ROUND(fm.return_on_assets * 100, 2) AS roa_percent,
    ROUND(fm.gross_margin * 100, 2) AS gross_margin_percent,
    ROUND(fm.operating_margin * 100, 2) AS operating_margin_percent,
    ROUND(fm.net_margin * 100, 2) AS net_margin_percent,
    ROUND(fm.debt_to_equity * 100, 2) AS debt_to_equity_percent,

    -- Bank ratios
    ROUND(fm.net_interest_margin * 100, 2) AS nim_percent,
    ROUND(fm.cost_to_income_ratio * 100, 2) AS cost_to_income_percent,
    ROUND(fm.loan_to_deposit_ratio * 100, 2) AS loan_to_deposit_percent,
    ROUND(fm.npl_ratio * 100, 2) AS npl_percent,

    -- Insurance ratios
    ROUND(fm.loss_ratio * 100, 2) AS loss_ratio_percent,
    ROUND(fm.combined_ratio * 100, 2) AS combined_ratio_percent,

    -- Liquidity
    fm.current_ratio,
    fm.quick_ratio,

    -- Status for natural language
    fm.profit_status,
    fm.liquidity_status,
    fm.leverage_status,
    fm.roe_status,
    fm.profitability_score,

    -- Flags
    fs.is_latest,
    fp.period_type = 'Annual' AS is_annual,
    fs.data_quality_score

FROM financial_statements fs
JOIN companies c ON fs.company_id = c.company_id
JOIN fiscal_periods fp ON fs.period_id = fp.period_id
LEFT JOIN sectors s ON c.sector_id = s.sector_id
LEFT JOIN company_sector_mapping csm ON c.ticker = csm.ticker
LEFT JOIN company_types ct ON csm.company_type_id = ct.company_type_id
LEFT JOIN financial_metrics fm ON fs.statement_id = fm.statement_id;

COMMENT ON MATERIALIZED VIEW company_financials IS 'Enhanced denormalized view with bank and insurance metrics - values in millions SAR and percentages';

-- =============================================================================
-- 7. CREATE INDEXES
-- =============================================================================

-- Materialized view indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_cf_ticker_period ON company_financials(ticker, fiscal_year, fiscal_quarter);
CREATE INDEX IF NOT EXISTS idx_cf_sector ON company_financials(sector);
CREATE INDEX IF NOT EXISTS idx_cf_institution_type ON company_financials(institution_type);
CREATE INDEX IF NOT EXISTS idx_cf_year ON company_financials(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_cf_latest ON company_financials(is_latest) WHERE is_latest = TRUE;
CREATE INDEX IF NOT EXISTS idx_cf_2024 ON company_financials(fiscal_year) WHERE fiscal_year = 2024;
CREATE INDEX IF NOT EXISTS idx_cf_profit_status ON company_financials(profit_status);

-- Financial statements indexes for new columns
CREATE INDEX IF NOT EXISTS idx_fs_net_interest_income ON financial_statements(net_interest_income DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_fs_gwp ON financial_statements(gross_written_premiums DESC NULLS LAST);

-- Financial metrics indexes for new ratios
CREATE INDEX IF NOT EXISTS idx_fm_nim ON financial_metrics(net_interest_margin DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_fm_combined_ratio ON financial_metrics(combined_ratio ASC NULLS LAST);

-- =============================================================================
-- 8. HELPER FUNCTIONS
-- =============================================================================

-- Get company type for a ticker
CREATE OR REPLACE FUNCTION get_company_type(p_ticker VARCHAR)
RETURNS VARCHAR AS $$
DECLARE
    v_type_code VARCHAR;
BEGIN
    SELECT ct.type_code
    INTO v_type_code
    FROM company_sector_mapping csm
    JOIN company_types ct ON csm.company_type_id = ct.company_type_id
    WHERE csm.ticker = p_ticker;

    RETURN COALESCE(v_type_code, 'STANDARD');
END;
$$ LANGUAGE plpgsql;

-- Get appropriate income metric for a company
CREATE OR REPLACE FUNCTION get_income_metric(p_ticker VARCHAR, p_fiscal_year INTEGER DEFAULT NULL)
RETURNS TABLE (
    metric_name VARCHAR,
    metric_value NUMERIC,
    fiscal_year INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        CASE
            WHEN get_company_type(p_ticker) = 'BANK' THEN 'Net Interest Income'::VARCHAR
            WHEN get_company_type(p_ticker) = 'INSURANCE' THEN 'Gross Written Premiums'::VARCHAR
            ELSE 'Revenue'::VARCHAR
        END,
        CASE
            WHEN get_company_type(p_ticker) = 'BANK' THEN fs.net_interest_income
            WHEN get_company_type(p_ticker) = 'INSURANCE' THEN fs.gross_written_premiums
            ELSE fs.revenue
        END,
        fp.fiscal_year
    FROM financial_statements fs
    JOIN companies c ON fs.company_id = c.company_id
    JOIN fiscal_periods fp ON fs.period_id = fp.period_id
    WHERE c.ticker = p_ticker
      AND (p_fiscal_year IS NULL OR fp.fiscal_year = p_fiscal_year)
      AND fs.is_latest = TRUE
    ORDER BY fp.fiscal_year DESC;
END;
$$ LANGUAGE plpgsql;

-- Get top banks by Net Interest Income
CREATE OR REPLACE FUNCTION get_top_banks_by_nii(
    p_year INTEGER DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    ticker VARCHAR,
    company_name VARCHAR,
    bank_type VARCHAR,
    net_interest_income_m NUMERIC,
    nim_percent NUMERIC,
    roe_percent NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.ticker,
        v.company_name,
        v.bank_type,
        v.net_interest_income_m,
        v.nim_percent,
        v.roe_percent
    FROM v_banks_latest v
    WHERE v.is_annual = TRUE
      AND (p_year IS NULL OR v.fiscal_year = p_year)
      AND v.is_latest = TRUE
    ORDER BY v.net_interest_income_m DESC NULLS LAST
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Get top insurance companies by Gross Written Premiums
CREATE OR REPLACE FUNCTION get_top_insurance_by_gwp(
    p_year INTEGER DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    ticker VARCHAR,
    company_name VARCHAR,
    insurance_type VARCHAR,
    gross_written_premiums_m NUMERIC,
    combined_ratio_percent NUMERIC,
    roe_percent NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.ticker,
        v.company_name,
        v.insurance_type,
        v.gross_written_premiums_m,
        v.combined_ratio_percent,
        v.roe_percent
    FROM v_insurance_latest v
    WHERE v.is_annual = TRUE
      AND (p_year IS NULL OR v.fiscal_year = p_year)
      AND v.is_latest = TRUE
    ORDER BY v.gross_written_premiums_m DESC NULLS LAST
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 9. REFRESH MATERIALIZED VIEW
-- =============================================================================

REFRESH MATERIALIZED VIEW company_financials;

-- =============================================================================
-- 10. VALIDATION QUERIES
-- =============================================================================

-- Show company type distribution
SELECT
    COALESCE(ct.type_name, 'Unmapped') AS company_type,
    COUNT(*) AS company_count
FROM companies c
LEFT JOIN company_sector_mapping csm ON c.ticker = csm.ticker
LEFT JOIN company_types ct ON csm.company_type_id = ct.company_type_id
GROUP BY ct.type_name
ORDER BY company_count DESC;

-- Show 2024 data availability by company type
SELECT
    COALESCE(ct.type_name, 'Standard') AS company_type,
    COUNT(DISTINCT c.ticker) AS total_companies,
    COUNT(DISTINCT CASE WHEN fp.fiscal_year = 2024 THEN c.ticker END) AS companies_with_2024_data,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN fp.fiscal_year = 2024 THEN c.ticker END) /
        NULLIF(COUNT(DISTINCT c.ticker), 0),
        2
    ) AS percent_coverage_2024
FROM companies c
LEFT JOIN company_sector_mapping csm ON c.ticker = csm.ticker
LEFT JOIN company_types ct ON csm.company_type_id = ct.company_type_id
LEFT JOIN financial_statements fs ON c.company_id = fs.company_id
LEFT JOIN fiscal_periods fp ON fs.period_id = fp.period_id
GROUP BY ct.type_name
ORDER BY total_companies DESC;

-- =============================================================================
-- End of Update Script
-- =============================================================================
