-- =============================================================================
-- TASI Financial Database Schema for Vanna AI + pgvector
-- Optimized for natural language queries and semantic search
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search

-- =============================================================================
-- DIMENSION TABLES (Normalized lookup tables)
-- =============================================================================

-- Sectors (GICS classification)
CREATE TABLE sectors (
    sector_id SERIAL PRIMARY KEY,
    sector_code VARCHAR(20) UNIQUE,
    sector_name VARCHAR(100) NOT NULL,
    sector_name_ar VARCHAR(100),  -- Arabic name for localization
    embedding VECTOR(1536),  -- OpenAI embedding for semantic search
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Companies (Master company data)
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    company_name_ar VARCHAR(200),  -- Arabic name
    sector_id INTEGER REFERENCES sectors(sector_id),
    company_type VARCHAR(50),  -- 'Industrial', 'Service', etc.
    size_category VARCHAR(20) CHECK (size_category IN ('Micro Cap', 'Small Cap', 'Mid Cap', 'Large Cap', 'Mega Cap')),
    description TEXT,
    embedding VECTOR(1536),  -- Company description embedding
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Fiscal periods (Standardized period definitions)
CREATE TABLE fiscal_periods (
    period_id SERIAL PRIMARY KEY,
    fiscal_year SMALLINT NOT NULL,
    fiscal_quarter VARCHAR(5) NOT NULL,  -- 'Q1', 'Q2', 'Q3', 'Q4', 'FY'
    period_type VARCHAR(10) NOT NULL CHECK (period_type IN ('Quarterly', 'Annual')),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_label VARCHAR(10) NOT NULL,  -- 'Q1 2024', 'FY2024'
    UNIQUE(fiscal_year, fiscal_quarter)
);

-- =============================================================================
-- FACT TABLE (Core financial statements)
-- =============================================================================

CREATE TABLE financial_statements (
    statement_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(company_id),
    period_id INTEGER NOT NULL REFERENCES fiscal_periods(period_id),
    filing_id VARCHAR(20) UNIQUE,

    -- Income Statement (SAR - Saudi Riyals)
    revenue NUMERIC(20,2),
    cost_of_sales NUMERIC(20,2),
    gross_profit NUMERIC(20,2),
    operating_profit NUMERIC(20,2),
    net_profit NUMERIC(20,2),
    interest_expense NUMERIC(20,2),

    -- Balance Sheet (SAR)
    total_assets NUMERIC(20,2),
    total_equity NUMERIC(20,2),
    total_liabilities NUMERIC(20,2),
    current_assets NUMERIC(20,2),
    current_liabilities NUMERIC(20,2),
    inventory NUMERIC(20,2),
    receivables NUMERIC(20,2),

    -- Cash Flow Statement (SAR)
    operating_cash_flow NUMERIC(20,2),
    capex NUMERIC(20,2),
    free_cash_flow NUMERIC(20,2),

    -- Working Capital
    working_capital NUMERIC(20,2),

    -- Data Quality
    data_quality_score SMALLINT CHECK (data_quality_score BETWEEN 0 AND 100),
    is_latest BOOLEAN DEFAULT FALSE,

    -- Source tracking
    source_file VARCHAR(100),
    loaded_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, period_id)
);

-- =============================================================================
-- COMPUTED METRICS TABLE (Financial ratios - stored for query performance)
-- =============================================================================

CREATE TABLE financial_metrics (
    metric_id SERIAL PRIMARY KEY,
    statement_id INTEGER NOT NULL REFERENCES financial_statements(statement_id) ON DELETE CASCADE,

    -- Profitability Ratios (stored as decimals: 0.15 = 15%)
    return_on_equity NUMERIC(10,6),
    return_on_assets NUMERIC(10,6),
    gross_margin NUMERIC(10,6),
    operating_margin NUMERIC(10,6),
    net_margin NUMERIC(10,6),

    -- Liquidity Ratios
    current_ratio NUMERIC(10,4),
    quick_ratio NUMERIC(10,4),

    -- Leverage Ratios
    debt_to_equity NUMERIC(10,6),
    debt_to_assets NUMERIC(10,6),
    interest_coverage_ratio NUMERIC(12,4),

    -- Efficiency Ratios
    asset_turnover NUMERIC(10,6),
    inventory_turnover NUMERIC(10,4),
    days_sales_outstanding NUMERIC(10,2),

    -- Derived Scores (for quick filtering)
    profitability_score SMALLINT CHECK (profitability_score BETWEEN 0 AND 100),

    -- Status Classifications (for natural language queries)
    profit_status VARCHAR(10) CHECK (profit_status IN ('Profit', 'Loss', 'N/A')),
    liquidity_status VARCHAR(15) CHECK (liquidity_status IN ('Strong', 'Moderate', 'Weak', 'Critical')),
    leverage_status VARCHAR(15) CHECK (leverage_status IN ('Low', 'Moderate', 'High', 'Critical')),
    roe_status VARCHAR(15) CHECK (roe_status IN ('Excellent', 'Good', 'Average', 'Weak', 'Negative', 'N/A')),

    -- Data Availability Flags
    has_cogs BOOLEAN DEFAULT FALSE,
    has_operating_profit BOOLEAN DEFAULT FALSE,
    has_cash_flow BOOLEAN DEFAULT FALSE,

    UNIQUE(statement_id)
);

-- =============================================================================
-- MATERIALIZED VIEW (Denormalized for Vanna AI queries)
-- =============================================================================

CREATE MATERIALIZED VIEW company_financials AS
SELECT
    -- Company Info
    c.ticker,
    c.company_name,
    c.company_type,
    c.size_category,
    s.sector_name AS sector,

    -- Period Info
    fp.fiscal_year,
    fp.fiscal_quarter,
    fp.period_type,
    fp.period_end,
    fp.period_label,

    -- Income Statement (in millions for readability)
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

    -- Key Ratios (as percentages for readability)
    ROUND(fm.return_on_equity * 100, 2) AS roe_percent,
    ROUND(fm.return_on_assets * 100, 2) AS roa_percent,
    ROUND(fm.gross_margin * 100, 2) AS gross_margin_percent,
    ROUND(fm.operating_margin * 100, 2) AS operating_margin_percent,
    ROUND(fm.net_margin * 100, 2) AS net_margin_percent,
    ROUND(fm.debt_to_equity * 100, 2) AS debt_to_equity_percent,

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
LEFT JOIN financial_metrics fm ON fs.statement_id = fm.statement_id;

-- =============================================================================
-- INDEXES (Optimized for common Vanna AI query patterns)
-- =============================================================================

-- Companies table
CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_sector ON companies(sector_id);
CREATE INDEX idx_companies_type ON companies(company_type);
CREATE INDEX idx_companies_size ON companies(size_category);
CREATE INDEX idx_companies_name_trgm ON companies USING gin(company_name gin_trgm_ops);

-- Financial statements
CREATE INDEX idx_fs_company_period ON financial_statements(company_id, period_id);
CREATE INDEX idx_fs_latest ON financial_statements(is_latest) WHERE is_latest = TRUE;
CREATE INDEX idx_fs_revenue ON financial_statements(revenue DESC NULLS LAST);
CREATE INDEX idx_fs_net_profit ON financial_statements(net_profit DESC NULLS LAST);

-- Fiscal periods
CREATE INDEX idx_fp_year ON fiscal_periods(fiscal_year);
CREATE INDEX idx_fp_type ON fiscal_periods(period_type);
CREATE INDEX idx_fp_year_quarter ON fiscal_periods(fiscal_year, fiscal_quarter);

-- Financial metrics
CREATE INDEX idx_fm_roe ON financial_metrics(return_on_equity DESC NULLS LAST);
CREATE INDEX idx_fm_profit_status ON financial_metrics(profit_status);
CREATE INDEX idx_fm_roe_status ON financial_metrics(roe_status);
CREATE INDEX idx_fm_profitability ON financial_metrics(profitability_score DESC NULLS LAST);

-- Materialized view indexes
CREATE UNIQUE INDEX idx_cf_ticker_period ON company_financials(ticker, fiscal_year, fiscal_quarter);
CREATE INDEX idx_cf_sector ON company_financials(sector);
CREATE INDEX idx_cf_year ON company_financials(fiscal_year);
CREATE INDEX idx_cf_latest ON company_financials(is_latest) WHERE is_latest = TRUE;

-- Vector indexes for semantic search
CREATE INDEX idx_companies_embedding ON companies USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX idx_sectors_embedding ON sectors USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- =============================================================================
-- HELPER FUNCTIONS (For Vanna AI natural language queries)
-- =============================================================================

-- Get latest financial data for a company
CREATE OR REPLACE FUNCTION get_company_latest(p_ticker VARCHAR)
RETURNS TABLE (LIKE company_financials) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM company_financials
    WHERE ticker = p_ticker AND is_latest = TRUE
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Get companies by profitability status
CREATE OR REPLACE FUNCTION get_profitable_companies(p_year INTEGER DEFAULT NULL)
RETURNS SETOF company_financials AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM company_financials
    WHERE profit_status = 'Profit'
      AND is_annual = TRUE
      AND (p_year IS NULL OR fiscal_year = p_year)
    ORDER BY roe_percent DESC NULLS LAST;
END;
$$ LANGUAGE plpgsql;

-- Semantic company search
CREATE OR REPLACE FUNCTION search_companies_semantic(
    p_query_embedding VECTOR(1536),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    ticker VARCHAR,
    company_name VARCHAR,
    sector_name VARCHAR,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.ticker,
        c.company_name,
        s.sector_name,
        1 - (c.embedding <=> p_query_embedding) AS similarity
    FROM companies c
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    WHERE c.embedding IS NOT NULL
    ORDER BY c.embedding <=> p_query_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTS (Critical for Vanna AI to understand the schema)
-- =============================================================================

COMMENT ON TABLE companies IS 'Master list of TASI-listed Saudi companies with ticker symbols and sector classifications';
COMMENT ON TABLE sectors IS 'GICS sector classifications for company categorization';
COMMENT ON TABLE fiscal_periods IS 'Standardized fiscal periods (quarterly and annual) for financial reporting';
COMMENT ON TABLE financial_statements IS 'Core financial statement data including income statement, balance sheet, and cash flow items';
COMMENT ON TABLE financial_metrics IS 'Calculated financial ratios and performance metrics derived from financial statements';
COMMENT ON MATERIALIZED VIEW company_financials IS 'Denormalized view combining all company financial data for easy querying - values in millions SAR and percentages';

COMMENT ON COLUMN companies.ticker IS 'Saudi stock exchange ticker symbol';
COMMENT ON COLUMN companies.embedding IS 'OpenAI text-embedding-3-small vector for semantic search';
COMMENT ON COLUMN companies.size_category IS 'Market capitalization category: Small Cap, Mid Cap, Large Cap';

COMMENT ON COLUMN financial_statements.revenue IS 'Total revenue in Saudi Riyals (SAR)';
COMMENT ON COLUMN financial_statements.net_profit IS 'Net profit after tax in Saudi Riyals (SAR)';
COMMENT ON COLUMN financial_statements.is_latest IS 'Flag indicating the most recent filing for this company';

COMMENT ON COLUMN financial_metrics.return_on_equity IS 'Return on Equity as decimal (0.15 = 15%)';
COMMENT ON COLUMN financial_metrics.profit_status IS 'Classification: Profit, Loss, or N/A';
COMMENT ON COLUMN financial_metrics.roe_status IS 'ROE performance: Excellent (>20%), Good (15-20%), Average (10-15%), Weak (0-10%), Negative (<0%)';

COMMENT ON COLUMN company_financials.revenue_millions IS 'Total revenue in millions of Saudi Riyals';
COMMENT ON COLUMN company_financials.roe_percent IS 'Return on Equity as percentage (15 = 15%)';
