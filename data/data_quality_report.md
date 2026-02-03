# TASI Financial Database - Data Quality Report

**Generated:** 2026-02-03
**Database:** TASI_financials_DB.csv
**Total Records:** 4,826
**Unique Companies:** 303

---

## Executive Summary

The TASI financial database contains significant data gaps, particularly for:
1. **2024 Annual Data** - 66 companies missing annual reports
2. **Bank/Insurance Revenue** - 37 financial institutions have NULL revenue (expected - they use different metrics)
3. **Core Financial Metrics** - Many companies missing operating profit and gross profit data

---

## 1. Companies Missing 2024 Annual Data

**Total Count:** 66 companies

### Major Companies Missing 2024 Data

| Ticker | Company Name | Priority |
|--------|--------------|----------|
| 2010 | Saudi Basic Industries Corp. (SABIC) | HIGH |
| 1120 | Al Rajhi Bank | HIGH |
| 1180 | The Saudi National Bank (SNB) | HIGH |
| 1050 | Banque Saudi Fransi | HIGH |
| 1080 | Arab National Bank | HIGH |

### Banks Missing 2024 Annual Data
- 1050: Banque Saudi Fransi
- 1080: Arab National Bank
- 1120: Al Rajhi Bank
- 1180: The Saudi National Bank

### Insurance Companies Missing 2024 Annual Data
| Ticker | Company Name |
|--------|--------------|
| 8010 | The Company for Cooperative Insurance |
| 8012 | Aljazira Takaful Taawuni Co. |
| 8020 | Malath Cooperative Insurance Co. |
| 8030 | The Mediterranean and Gulf Insurance and Reinsurance Co. |
| 8040 | Allianz Saudi Fransi Cooperative Insurance Co. |
| 8050 | Salama Cooperative Insurance Co. |
| 8060 | Walaa Cooperative Insurance Co. |
| 8070 | Arabian Shield Cooperative Insurance Co. |
| 8100 | Saudi Arabian Cooperative Insurance Co. |
| 8120 | Gulf Union Cooperative Insurance Co. |
| 8150 | Allied Cooperative Insurance Group |
| 8160 | Arabia Insurance Cooperative Co. |
| 8170 | Al-Etihad Cooperative Insurance Co. |
| 8180 | Al Sagr Cooperative Insurance Co. |
| 8190 | United Cooperative Assurance Co. |
| 8200 | Saudi Re for Cooperative Reinsurance Co. |
| 8230 | Al-Rajhi Company for Cooperative Insurance |
| 8240 | CHUBB Arabia Cooperative Insurance Co. |
| 8250 | AXA Cooperative Insurance Co. |
| 8260 | Gulf General Cooperative Insurance Co. |
| 8280 | Al Alamiya for Cooperative Insurance Co. |
| 8300 | Wataniya Insurance Co. |
| 8310 | Amana Cooperative Insurance Co. |
| 8311 | Saudi Enaya Cooperative Insurance Co. |

### Industrial Companies Missing 2024 Annual Data
| Ticker | Company Name |
|--------|--------------|
| 2010 | Saudi Basic Industries Corp. (SABIC) |
| 2020 | SABIC Agri-Nutrients Co. / Saudi Arabian Fertilizer Co. |
| 2080 | National Gas and Industrialization Co. |
| 2360 | Saudi Vitrified Clay Pipes Co. |
| 2370 | Middle East Specialized Cables Co. |
| 3002 | Najran Cement Co. |
| 1320 | Saudi Steel Pipe Co. |

### Other Companies Missing 2024 Annual Data
| Ticker | Company Name |
|--------|--------------|
| 4004 | Dallah Healthcare Co. |
| 4021 | Canadian Medical Center Co. |
| 4145 | Obeikan Glass Co. |
| 4146 | Gas Arabian Services Co. |
| 4150 | Arriyadh Development Co. |
| 4191 | Abdullah Saad Mohammed Abo Moati for Bookstores Co. |
| 4230 | Red Sea International Co. |
| 4290 | Alkhaleej Training and Education Co. |
| 4291 | National Company for Learning and Education |
| 4292 | Ataa Educational Co. |
| 6012 | Raydan Food Co. |
| 6040 | Tabuk Agricultural Development Co. |
| 6070 | Al-Jouf Agricultural Development Co. |
| 7204 | Perfect Presentation for Commercial Services Co. |
| 7211 | Saudi Azm for Communication and Information Technology Co. |

### Nomu/Parallel Market Companies (9xxx) Missing 2024 Data
| Ticker | Company Name |
|--------|--------------|
| 9506 | Raydan Food Co. |
| 9511 | Sumou Real Estate Co. |
| 9512 | Riyadh Cement Co. |
| 9519 | Banan Real Estate Co. |
| 9524 | Advance International Company for Communication and IT |
| 9526 | Jahez International Company for IT |
| 9534 | Saudi Azm for Communication and IT Co. |
| 9545 | International Human Resources Co. |
| 9547 | Rawasi Albina Investment Co. |
| 9564 | Horizon Food Co. |
| 9565 | Meyar Co. |
| 9572 | Al-Razi Medical Co. |
| 9598 | Al Mohafaza Company for Education |
| 9636 | Al Kuzama Trading Co. |
| 9649 | Jamjoom Fashion Trading Co. |

---

## 2. Companies with NULL Revenue

**Total Count:** 62 companies with NULL revenue values

### Reason: Financial Institutions Use Different Metrics

Banks and insurance companies do not report traditional "revenue" as they operate on:
- **Banks:** Net Interest Income, Fee Income, Trading Income
- **Insurance:** Gross Written Premiums, Net Earned Premiums

### Banks with NULL Revenue (Expected)
| Ticker | Company Name |
|--------|--------------|
| 1010 | Riyad Bank |
| 1020 | Bank Aljazira |
| 1030 | Saudi Investment Bank |
| 1050 | Banque Saudi Fransi |
| 1060 | Saudi Awwal Bank / Saudi British Bank |
| 1080 | Arab National Bank |
| 1120 | Al Rajhi Bank |
| 1140 | Bank Albilad |
| 1150 | Alinma Bank |
| 1180 | The Saudi National Bank |

### Insurance Companies with NULL Revenue (Expected)
All 8xxx ticker companies (see Section 1 for full list)

### Non-Financial Companies with NULL Revenue (Data Issue)
| Ticker | Company Name | Issue |
|--------|--------------|-------|
| 1182 | Amlak International Finance Co. | Finance company - expected |
| 1183 | SHL Finance Co. / Saudi Home Loans | Finance company - expected |
| 1210 | Basic Chemical Industries Co. | DATA ISSUE |
| 1320 | Saudi Steel Pipe Co. | DATA ISSUE |
| 1323 | United Carton Industries Co. | DATA ISSUE |
| 1820 | Abdulmohsen Alhokair Group | DATA ISSUE |
| 1831 | Maharah Human Resources Co. | DATA ISSUE |
| 2010 | Saudi Basic Industries Corp. (SABIC) | DATA ISSUE |
| 2020 | Saudi Arabian Fertilizer Co. | DATA ISSUE |
| 2030 | Saudi Arabia Refineries Co. | DATA ISSUE |
| 2040 | Saudi Ceramic Co. | DATA ISSUE |
| 2240 | Advanced Building Industries Co. | DATA ISSUE |
| 2270 | Saudia Dairy and Foodstuff Co. | DATA ISSUE |
| 2280 | Almarai Co. | DATA ISSUE |
| 2370 | Middle East Specialized Cables Co. | DATA ISSUE |
| 3002 | Najran Cement Co. | DATA ISSUE |
| 3008 | Al Kathiri Holding Co. | DATA ISSUE |
| 3090 | Tabuk Cement Co. | DATA ISSUE |
| 3091 | Al Jouf Cement Co. | DATA ISSUE |
| 4001 | Abdullah Al Othaim Markets Co. | DATA ISSUE |
| 4004 | Dallah Healthcare Co. | DATA ISSUE |
| 4050 | Saudi Automotive Services Co. | DATA ISSUE |
| 4070 | Tihama Advertising Co. | DATA ISSUE |
| 4072 | MBC Group Co. | DATA ISSUE |
| 4130 | Saudi Darb Investment Co. | DATA ISSUE |
| 4164 | Nahdi Medical Co. | DATA ISSUE |
| 4170 | Tourism Enterprise Co. | DATA ISSUE |
| 4191 | Abdullah Saad Mohammed Abo Moati | DATA ISSUE |
| 4200 | Aldrees Petroleum and Transport | DATA ISSUE |
| 4220 | Emaar The Economic City | DATA ISSUE |
| 4230 | Red Sea International Co. | DATA ISSUE |
| 4240 | Fawaz Abdulaziz Alhokair Co. | DATA ISSUE |
| 4261 | Theeb Rent a Car Co. | DATA ISSUE |
| 4265 | Cherry Trading Co. | DATA ISSUE |
| 4280 | Kingdom Holding Co. | DATA ISSUE |
| 4292 | Ataa Educational Co. | DATA ISSUE |

---

## 3. Companies with Incomplete Financial Metrics

### Missing Total Assets and Total Equity (Annual 2023-2024)
**Count:** 8 companies (All banks - data structure issue)

| Ticker | Company Name |
|--------|--------------|
| 1010 | Riyad Bank |
| 1020 | Bank Aljazira |
| 1030 | Saudi Investment Bank |
| 1060 | Saudi Awwal Bank |
| 1120 | Al Rajhi Bank |
| 1140 | Bank Albilad |
| 1150 | Alinma Bank |
| 1180 | The Saudi National Bank |

### Missing Operating Profit (Annual 2023-2024)
**Count:** 92 companies

This is expected for:
- Banks (use different income statement structure)
- Insurance companies (use different income statement structure)
- Some service companies

### Missing Gross Profit (Annual 2023-2024)
**Count:** 92 companies

This is expected for:
- Financial institutions (no COGS concept)
- Service companies (may report as operating expenses)

---

## 4. Data Quality Score Analysis

| Metric | Value |
|--------|-------|
| Mean Score | 78.9 |
| Median Score | 93.0 |
| Min Score | 0.0 |
| Max Score | 100.0 |

### Companies with Critically Low Quality Scores (< 20)

| Ticker | Company Name | Score | Issue |
|--------|--------------|-------|-------|
| 4240 | Fawaz Abdulaziz Alhokair Co. | 0 | Complete data missing |
| 1080 | Arab National Bank | 7 | Bank - different metrics needed |
| 1140 | Bank Albilad | 7 | Bank - different metrics needed |
| 1050 | Banque Saudi Fransi | 7 | Bank - different metrics needed |
| 1182 | Amlak International Finance Co. | 7 | Finance company |
| 1020 | Bank Aljazira | 7 | Bank - different metrics needed |
| 1120 | Al Rajhi Bank | 7 | Bank - different metrics needed |
| 1183 | Saudi Home Loans Co. | 7 | Finance company |
| 1060 | Saudi British Bank / Saudi Awwal Bank | 7 | Bank - different metrics needed |
| 1030 | Saudi Investment Bank | 7 | Bank - different metrics needed |
| 1180 | The Saudi National Bank | 7 | Bank - different metrics needed |
| 1150 | Alinma Bank | 7 | Bank - different metrics needed |
| 1010 | Riyad Bank | 7 | Bank - different metrics needed |
| 4072 | MBC Group Co. | 7 | Media company |
| 8030 | Med & Gulf Insurance | 13 | Insurance - different metrics |
| 8060 | Walaa Cooperative Insurance | 13 | Insurance - different metrics |

---

## 5. Recommendations for Data Sourcing

### Priority 1: Major Companies Missing 2024 Data
1. **SABIC (2010)** - Source from Tadawul annual reports or company IR website
2. **Al Rajhi Bank (1120)** - Source from bank's published financials (use bank metrics)
3. **Saudi National Bank (1180)** - Source from bank's published financials (use bank metrics)

### Priority 2: Fix Data Quality for Banks
Banks need different metrics extracted:
- Net Interest Income (replaces Revenue)
- Net Interest Margin
- Cost-to-Income Ratio
- Loan-to-Deposit Ratio
- Non-Performing Loan Ratio
- Capital Adequacy Ratio
- Tier 1 Capital Ratio

### Priority 3: Fix Data Quality for Insurance
Insurance companies need different metrics:
- Gross Written Premiums (replaces Revenue)
- Net Earned Premiums
- Loss Ratio
- Combined Ratio
- Investment Income
- Solvency Ratio

### Priority 4: Industrial Companies Data Gaps
Source missing data from:
- Tadawul official filings
- Company investor relations pages
- Argaam financial data
- Bloomberg/Reuters terminals

### Data Sources
1. **Tadawul (Saudi Exchange):** https://www.tadawul.com.sa
2. **Argaam:** https://www.argaam.com
3. **Company IR websites**
4. **SAMA (Saudi Central Bank)** - for bank data
5. **Insurance Authority** - for insurance company data

---

## 6. Database Schema Issues

### Identified Problems
1. **sector_gics** column is NULL for all records
2. **company_type** only has 3 values: Industrial, Service, Bank/Insurance
3. Duplicate ticker entries (e.g., 1060 has both "Saudi Awwal Bank" and "Saudi British Bank")
4. Some Nomu market companies (9xxx) have incomplete historical data

### Recommended Actions
1. Populate sector_gics with GICS sector codes
2. Split company_type into more granular categories
3. Resolve duplicate tickers (company name changes)
4. Add unit_multiplier field for different reporting scales

---

## Appendix: Data Availability Matrix

| Fiscal Year | Annual Records | Companies with Data |
|-------------|----------------|---------------------|
| 2018 | ~50 | Limited coverage |
| 2019 | ~80 | Moderate coverage |
| 2020 | ~200 | Good coverage |
| 2021 | ~250 | Good coverage |
| 2022 | ~280 | Good coverage |
| 2023 | ~300 | Excellent coverage |
| 2024 | ~239 | 66 companies missing |

---

*Report generated by TASI Data Quality Analysis System*
