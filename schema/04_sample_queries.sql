-- =============================================================================
-- TASI Financial Database - Sample Queries for Vanna AI Testing
-- Use these to verify the database is working correctly
-- =============================================================================

-- -----------------------------------------------------------------------------
-- BASIC DATA EXPLORATION
-- -----------------------------------------------------------------------------

-- 1. Count records
SELECT 'companies' as table_name, COUNT(*) as record_count FROM companies
UNION ALL
SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL
SELECT 'fiscal_periods', COUNT(*) FROM fiscal_periods
UNION ALL
SELECT 'financial_statements', COUNT(*) FROM financial_statements
UNION ALL
SELECT 'financial_metrics', COUNT(*) FROM financial_metrics;

-- 2. List all companies with their sectors
SELECT c.ticker, c.company_name, s.sector_name, c.company_type, c.size_category
FROM companies c
LEFT JOIN sectors s ON c.sector_id = s.sector_id
ORDER BY c.company_name;

-- 3. List all sectors with company counts
SELECT s.sector_name, COUNT(c.company_id) as company_count
FROM sectors s
LEFT JOIN companies c ON s.sector_id = c.sector_id
GROUP BY s.sector_name
ORDER BY company_count DESC;

-- 4. List all fiscal periods
SELECT fiscal_year, fiscal_quarter, period_type, period_start, period_end, period_label
FROM fiscal_periods
ORDER BY fiscal_year DESC, fiscal_quarter;

-- -----------------------------------------------------------------------------
-- PROFITABILITY ANALYSIS
-- -----------------------------------------------------------------------------

-- 5. Top 20 companies by ROE (latest annual)
SELECT ticker, company_name, sector, roe_percent, net_margin_percent, profit_status
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
ORDER BY roe_percent DESC NULLS LAST
LIMIT 20;

-- 6. Most profitable by net income
SELECT ticker, company_name, sector, net_profit_millions, revenue_millions,
       ROUND(net_profit_millions / NULLIF(revenue_millions, 0) * 100, 2) as actual_margin
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
ORDER BY net_profit_millions DESC NULLS LAST
LIMIT 20;

-- 7. Companies with excellent ROE
SELECT ticker, company_name, sector, roe_percent, roe_status
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE AND roe_status = 'Excellent'
ORDER BY roe_percent DESC;

-- 8. Loss-making companies
SELECT ticker, company_name, sector, net_profit_millions, net_margin_percent
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE AND profit_status = 'Loss'
ORDER BY net_profit_millions ASC;

-- -----------------------------------------------------------------------------
-- SECTOR ANALYSIS
-- -----------------------------------------------------------------------------

-- 9. Sector performance summary
SELECT
    sector,
    COUNT(DISTINCT ticker) as companies,
    ROUND(AVG(revenue_millions), 2) as avg_revenue_m,
    ROUND(SUM(revenue_millions), 2) as total_revenue_m,
    ROUND(AVG(roe_percent), 2) as avg_roe_pct,
    ROUND(AVG(net_margin_percent), 2) as avg_net_margin_pct,
    SUM(CASE WHEN profit_status = 'Profit' THEN 1 ELSE 0 END) as profitable,
    SUM(CASE WHEN profit_status = 'Loss' THEN 1 ELSE 0 END) as loss_making
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
GROUP BY sector
ORDER BY total_revenue_m DESC NULLS LAST;

-- 10. Sector comparison by liquidity
SELECT
    sector,
    COUNT(DISTINCT ticker) as companies,
    ROUND(AVG(current_ratio), 2) as avg_current_ratio,
    ROUND(AVG(quick_ratio), 2) as avg_quick_ratio,
    SUM(CASE WHEN liquidity_status = 'Strong' THEN 1 ELSE 0 END) as strong_liquidity,
    SUM(CASE WHEN liquidity_status = 'Weak' OR liquidity_status = 'Critical' THEN 1 ELSE 0 END) as weak_liquidity
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
GROUP BY sector
ORDER BY avg_current_ratio DESC NULLS LAST;

-- -----------------------------------------------------------------------------
-- LEVERAGE & RISK ANALYSIS
-- -----------------------------------------------------------------------------

-- 11. Most leveraged companies
SELECT ticker, company_name, sector, debt_to_equity_percent, leverage_status,
       total_liabilities_millions, total_equity_millions
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
ORDER BY debt_to_equity_percent DESC NULLS LAST
LIMIT 20;

-- 12. Low leverage, high profitability (quality companies)
SELECT ticker, company_name, sector, roe_percent, debt_to_equity_percent,
       leverage_status, roe_status
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
  AND leverage_status = 'Low'
  AND roe_status IN ('Excellent', 'Good')
ORDER BY roe_percent DESC;

-- 13. Companies at financial risk (high leverage + weak liquidity)
SELECT ticker, company_name, sector,
       debt_to_equity_percent, leverage_status,
       current_ratio, liquidity_status,
       profit_status
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
  AND (leverage_status = 'High' OR liquidity_status IN ('Weak', 'Critical'))
ORDER BY debt_to_equity_percent DESC NULLS LAST;

-- -----------------------------------------------------------------------------
-- TIME SERIES ANALYSIS
-- -----------------------------------------------------------------------------

-- 14. Year-over-year summary
SELECT
    fiscal_year,
    COUNT(DISTINCT ticker) as companies_reporting,
    ROUND(SUM(revenue_millions), 2) as total_revenue_m,
    ROUND(SUM(net_profit_millions), 2) as total_profit_m,
    ROUND(AVG(roe_percent), 2) as avg_roe_pct
FROM company_financials
WHERE is_annual = TRUE
GROUP BY fiscal_year
ORDER BY fiscal_year;

-- 15. Specific company trend (replace ticker)
SELECT fiscal_year, fiscal_quarter, period_type,
       revenue_millions, net_profit_millions, roe_percent, profit_status
FROM company_financials
WHERE ticker = '9541'
ORDER BY fiscal_year, fiscal_quarter;

-- 16. Quarterly vs Annual comparison
SELECT
    period_type,
    COUNT(*) as records,
    ROUND(AVG(revenue_millions), 2) as avg_revenue_m,
    ROUND(AVG(roe_percent), 2) as avg_roe_pct
FROM company_financials
GROUP BY period_type;

-- -----------------------------------------------------------------------------
-- SIZE ANALYSIS
-- -----------------------------------------------------------------------------

-- 17. Performance by company size
SELECT
    size_category,
    COUNT(DISTINCT ticker) as companies,
    ROUND(AVG(revenue_millions), 2) as avg_revenue_m,
    ROUND(AVG(total_assets_millions), 2) as avg_assets_m,
    ROUND(AVG(roe_percent), 2) as avg_roe_pct,
    ROUND(AVG(net_margin_percent), 2) as avg_net_margin_pct
FROM company_financials
WHERE is_latest = TRUE AND is_annual = TRUE
GROUP BY size_category
ORDER BY avg_revenue_m DESC NULLS LAST;

-- -----------------------------------------------------------------------------
-- SPECIFIC COMPANY LOOKUP
-- -----------------------------------------------------------------------------

-- 18. Full financial profile for a company
SELECT *
FROM company_financials
WHERE ticker = '4191' AND is_annual = TRUE
ORDER BY fiscal_year DESC;

-- 19. Search companies by name
SELECT DISTINCT ticker, company_name, sector, size_category
FROM company_financials
WHERE company_name ILIKE '%real estate%'
ORDER BY company_name;

-- 20. Latest data for all companies
SELECT ticker, company_name, sector, fiscal_year, fiscal_quarter,
       revenue_millions, net_profit_millions, roe_percent, profit_status
FROM company_financials
WHERE is_latest = TRUE
ORDER BY company_name;

-- -----------------------------------------------------------------------------
-- DATA QUALITY CHECKS
-- -----------------------------------------------------------------------------

-- 21. Records with low data quality
SELECT ticker, company_name, fiscal_year, fiscal_quarter, data_quality_score
FROM company_financials
WHERE data_quality_score < 70
ORDER BY data_quality_score;

-- 22. Missing key metrics
SELECT ticker, company_name, fiscal_year,
       CASE WHEN revenue_millions IS NULL THEN 'Missing Revenue' END as issue1,
       CASE WHEN net_profit_millions IS NULL THEN 'Missing Net Profit' END as issue2,
       CASE WHEN roe_percent IS NULL THEN 'Missing ROE' END as issue3
FROM company_financials
WHERE is_annual = TRUE
  AND (revenue_millions IS NULL OR net_profit_millions IS NULL OR roe_percent IS NULL)
ORDER BY fiscal_year DESC, ticker;
