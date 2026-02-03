# Changelog

All notable changes to the TASI Financial AI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-02-03

### 🎯 Major Update: FY2024 Financial Data Integration

This release represents a significant expansion of the database with comprehensive FY2024 financial data across multiple sectors.

### Added

#### Data Extraction & Processing
- **36 new company records** for Fiscal Year 2024 extracted from Excel source files
  - 6 Banks (100% coverage of available FYE_2024 files)
  - 13 Industrial companies (cement, manufacturing, industrial investment)
  - 14 Other sectors (healthcare, retail, finance, telecom, real estate)
  - 3 Additional companies pending review (unit verification needed)

- **New data extraction pipeline** with automated validation:
  - Multi-sector JSON extraction from Excel workbooks
  - Automated balance sheet validation (Assets = Liabilities + Equity)
  - Unit standardization detection and normalization
  - Data quality scoring and confidence metrics
  - Comprehensive validation reporting

- **Data files added**:
  - `data/extracted/banks_2024.json` - 6 banking sector companies
  - `data/extracted/industrial_2024.json` - 16 industrial companies
  - `data/extracted/other_sectors_2024.json` - 17 diversified sector companies
  - `data/extracted/insurance_2024.json` - 24 companies (excluded from insert - stale data)
  - `data/extracted/CONSOLIDATED_financials.json` - All extracted records
  - `data/extracted/VALIDATION_REPORT.md` - Comprehensive QA analysis

- **Company classification system**:
  - `data/company_classifications.json` - Sector mapping for all TASI companies
  - Supports Banks, Insurance, Industrial, Telecom, Healthcare, Retail, Real Estate, Finance, Media, Consumer, Services

#### Database Schema Enhancements
- **New sector-specific views**:
  - `vw_banks_summary` - Banking sector key metrics
  - `vw_industrial_summary` - Industrial sector performance
  - `vw_latest_financials` - Most recent fiscal year data per company

- **Database backup system**:
  - Pre-migration backup: `data/backup/financial_data_backup_pre_migration.csv`
  - Rollback capability for data safety

#### Validation & Quality Assurance
- **New validation script**: `scripts/validate_extraction.py`
  - Automated record count verification
  - Data integrity checks (NULL validation, duplicate detection)
  - Balance sheet equation validation with 5% tolerance
  - Data quality metrics (negative equity detection, ratio analysis)
  - Schema validation for views
  - JSON report generation

- **Quality metrics implemented**:
  - Confidence scoring system (0-100)
  - Automated rejection criteria (negative equity, missing data)
  - Balance sheet variance detection
  - Unit consistency analysis

#### Application Updates
- Enhanced Streamlit UI for better data exploration
- Improved sector-based filtering and analysis
- Updated example questions to leverage new FY2024 data

### Changed
- Database schema updated to support expanded sector classifications
- Migration scripts enhanced with validation and rollback capabilities
- Improved error handling in data processing pipelines
- Updated documentation to reflect new data sources and validation processes

### Fixed
- Unit inconsistency detection between "thousands" and "actuals"
- Balance sheet variance validation for high-value records
- Data type handling for mixed numeric formats

### Known Issues

#### Missing Data - High Priority
- **4 Major Banks** missing FYE_2024 files (not yet extracted):
  - 1050: Banque Saudi Fransi
  - 1080: Arab National Bank
  - 1120: Al Rajhi Bank (largest Islamic bank)
  - 1180: The Saudi National Bank (largest bank by assets)

- **2 Major Industrial Companies** missing:
  - 2010: SABIC (largest petrochemical company)
  - 2020: SABIC Agri-Nutrients

#### Data Quality Issues
- **Insurance Sector** (24 companies): All FY2024 data unavailable
  - Current data ranges from FY2017-FY2022 (2-7 years stale)
  - Excluded from FY2024 database insertion
  - Requires re-extraction with updated source files

- **3 Companies** flagged for review:
  - 4142: Riyadh Cables Group (Revenue/COGS mismatch - possible data entry error)
  - 4013: Dr. Sulaiman Al Habib Medical (Unit verification needed - values appear to be in millions not thousands)
  - 3003, 3050: City Cement, Southern Province Cement (Missing current assets/liabilities)

- **1 Company** rejected:
  - 4240: Fawaz Alhokair Co (Negative equity - liabilities exceed assets)

### Data Statistics

#### Insertion Summary
| Category | Companies Extracted | Insert-Ready | Excluded/Pending |
|----------|---------------------|--------------|------------------|
| Banks | 6 | 6 (100%) | 0 |
| Insurance | 24 | 0 (0%) | 24 (stale data) |
| Industrial | 16 | 13 (81%) | 3 (review needed) |
| Other Sectors | 17 | 14 (82%) | 3 (1 rejected, 2 review) |
| **TOTAL** | **63** | **33** | **30** |

#### Data Coverage by Fiscal Year
- FY2024: 36 companies (33 inserted, 3 pending review)
- FY2023 and earlier: Historical baseline data

### Technical Details

#### Dependencies
- No new Python dependencies required
- Existing requirements.txt supports all new features
- PostgreSQL views compatible with existing schema

#### Database
- Connection: PostgreSQL 15+ (Docker: localhost:5433)
- Total records after migration: Historical baseline + 33 new FY2024 records
- Backup strategy: CSV export before each migration

#### Validation Thresholds
- Balance sheet tolerance: 5% variance allowed
- Confidence score minimum: 80/100 for auto-insertion
- Data freshness requirement: FY2024 only (except historical comparison data)

### Migration Notes

**Pre-Migration Checklist:**
- ✅ Database backup created
- ✅ Schema updates deployed (views)
- ✅ Data validation completed
- ✅ Balance sheet integrity verified
- ✅ Duplicate detection passed

**Post-Migration Verification:**
- Run `python scripts/validate_extraction.py` to verify data integrity
- Check `data/extracted/VALIDATION_RESULTS.json` for detailed metrics
- Review sector-specific views: `vw_banks_summary`, `vw_industrial_summary`

### Future Enhancements

**Planned for v2.1.0:**
- Extraction of missing major banks (Al Rajhi, SNB, BSF, ANB)
- SABIC and SABIC Agri-Nutrients integration
- Insurance sector FY2024 data (when available)
- Unit normalization automation
- Enhanced data quality scoring

**Planned for v2.2.0:**
- Time-series analysis across multiple fiscal years
- Peer comparison dashboards
- Automated anomaly detection
- API endpoints for data access

### Contributors
- Data Extraction: Automated QA Process
- Validation: QA Engineering Team
- Schema Design: Database Architecture Team
- Documentation: Project Documentation Team

### References
- Validation Report: `data/extracted/VALIDATION_REPORT.md`
- Backup Data: `data/backup/financial_data_backup_pre_migration.csv`
- Classification Schema: `data/company_classifications.json`

---

## [1.0.0] - 2025-12-15

### Initial Release
- Basic database schema for TASI financial data
- Streamlit application for SQL query generation
- Vanna AI integration for natural language queries
- PostgreSQL backend with Docker support
- Initial dataset with historical financial data

---

**Legend:**
- 🎯 Major feature
- ✨ Enhancement
- 🐛 Bug fix
- 📝 Documentation
- ⚠️ Known issue
- 🔧 Technical change
