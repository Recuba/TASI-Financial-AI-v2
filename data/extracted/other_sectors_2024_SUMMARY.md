# Financial Data Extraction Summary - Other Sectors 2024

**Extraction Date:** 2026-02-03
**Source:** Saudi Financial Chat Database (xlsx_companies folder)
**Output File:** `C:\Users\User\venna-ai\data\extracted\other_sectors_2024.json`

## Extraction Results

### Successfully Extracted: 17 of 20 Companies

All 17 companies have complete financial data with 5+ metrics extracted.

#### By Sector:

**Finance Sector (3 companies)**
- ✅ Nayifat Finance Co (4081) - 7 metrics
- ✅ SHL Finance Co (1183) - 8 metrics
- ✅ Amlak International Finance Co (1182) - 8 metrics

**Telecom Sector (2 companies)**
- ✅ Etihad Atheeb Telecommunication Co (7040) - 9 metrics
- ✅ Saudi Tadawul Group Holding Co (1111) - 8 metrics

**Retail Sector (4 companies)**
- ✅ BinDawood Holding Co (4161) - 9 metrics
- ✅ Jarir Marketing Co (4190) - 9 metrics
- ✅ Nahdi Medical Co (4164) - 8 metrics
- ✅ Fawaz Abdulaziz Alhokair Co (4240) - 8 metrics

**Healthcare Sector (2 companies)**
- ✅ Canadian Medical Center Co (4021) - 9 metrics
- ✅ Dr. Sulaiman Al Habib Medical Services Group (4013) - 9 metrics

**Consumer Sector (2 companies)**
- ✅ Almarai Co (2280) - 7 metrics
- ✅ Almunajem Foods Co (6001) - 9 metrics

**Services Sector (2 companies)**
- ✅ Aldrees Petroleum and Transport Services Co (4200) - 9 metrics
- ✅ Leejam Sports Co (1830) - 8 metrics

**Real Estate Sector (1 company)**
- ✅ Emaar The Economic City (4220) - 8 metrics

**Media Sector (1 company)**
- ✅ MBC Group Co (4072) - 8 metrics

### Missing FYE_2024 Files: 3 Companies

1. **Abdullah Al Othaim Markets Co (4001)**
   - Status: FYE_2024 file not available
   - Latest available: FYE_2023, plus Q1/Q3/Q4 2024 quarterly files
   - Recommendation: Use Q4 2024 quarterly file or wait for FYE_2024 release

2. **Dallah Healthcare Co (4004)**
   - Status: No 2024 data available
   - Latest available: 2023 Q2
   - Recommendation: Data appears outdated; verify company status

3. **Kingdom Holding Co (4280)**
   - Status: FYE_2024 file not available
   - Latest available: Q1/Q2/Q3 2024 quarterly files
   - Recommendation: Use Q3 2024 quarterly file or wait for FYE_2024 release

## Financial Metrics Extracted

The extraction script captured the following metrics where available:

### Income Statement Metrics:
- Revenue / Sales (or Finance Income for finance companies)
- Gross Profit
- Operating Income / EBIT
- Profit before Zakat and Tax
- Net Income / Net Profit

### Balance Sheet Metrics:
- Total Assets
- Total Liabilities
- Total Equity
- Cash and Cash Equivalents
- Current Assets (where reported separately)
- Current Liabilities (where reported separately)

## Reporting Units

The extraction detected three types of reporting units:

1. **Thousands SAR** - Most finance and smaller companies (e.g., Nayifat Finance: total assets 2,064,758 thousands)
2. **Millions SAR** - Some larger companies with smaller reported numbers
3. **Units (SAR)** - Large companies reporting in individual riyals (e.g., Etihad Atheeb: revenue 1,016,118,736)

## Data Quality Notes

1. **Finance Companies**: Used "Finance Income" as revenue equivalent, which is appropriate for their business model
2. **Statement Formats**: Successfully handled both:
   - Nature of Expense format (code [300300])
   - Function of Expense format (code [300400])
3. **Balance Sheet Formats**: Successfully handled both:
   - Order of Liquidity format (code [300100])
   - Current/Non-Current format (code [300200])

## Technical Implementation

- **Extraction Method**: Python pandas for Excel reading
- **Data Source**: XBRL-formatted financial statements from Tadawul
- **Section Detection**: Automated detection of income statement and balance sheet sections using XBRL codes
- **Value Parsing**: Handled string-formatted numbers with comma separators
- **Error Handling**: Graceful fallback for missing sections or metrics

## Next Steps

1. **Database Upload**: This data can be uploaded to the TASI database to fill missing 2024 annual data
2. **Missing Companies**: Consider extracting Q3/Q4 2024 quarterly data for Abdullah Al Othaim and Kingdom Holding
3. **Validation**: Cross-reference extracted values with Tadawul official statements
4. **Reporting Units**: Standardize all values to a consistent unit (e.g., thousands SAR) before database upload

## File Location

**JSON Output:** `C:\Users\User\venna-ai\data\extracted\other_sectors_2024.json`

This file can be directly imported into database processing scripts or used for data quality validation.
