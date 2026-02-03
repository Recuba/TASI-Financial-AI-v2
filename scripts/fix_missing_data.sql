-- ============================================================================
-- TASI Financial Database - Data Quality Fix Script
-- Generated: 2026-02-03
-- Purpose: Update company unit multipliers, sector classifications, and flag
--          data quality issues
-- ============================================================================

-- ============================================================================
-- SECTION 1: CREATE/UPDATE company_unit_multipliers TABLE
-- ============================================================================

-- Drop and recreate the table if it exists
DROP TABLE IF EXISTS company_unit_multipliers;

CREATE TABLE company_unit_multipliers (
    ticker INT PRIMARY KEY,
    company_name VARCHAR(255),
    unit_multiplier DECIMAL(18,6) DEFAULT 1.0,
    currency VARCHAR(10) DEFAULT 'SAR',
    reporting_standard VARCHAR(50),
    notes TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert ALL known multipliers for TASI companies
-- Most companies report in SAR (thousands), some in millions

-- Banks (typically report in thousands SAR)
INSERT INTO company_unit_multipliers (ticker, company_name, unit_multiplier, reporting_standard, notes) VALUES
(1010, 'Riyad Bank', 1000, 'IFRS', 'Reports in thousands SAR'),
(1020, 'Bank Aljazira', 1000, 'IFRS', 'Reports in thousands SAR'),
(1030, 'Saudi Investment Bank', 1000, 'IFRS', 'Reports in thousands SAR'),
(1050, 'Banque Saudi Fransi', 1000, 'IFRS', 'Reports in thousands SAR'),
(1060, 'Saudi Awwal Bank', 1000, 'IFRS', 'Reports in thousands SAR - formerly Saudi British Bank'),
(1080, 'Arab National Bank', 1000, 'IFRS', 'Reports in thousands SAR'),
(1120, 'Al Rajhi Bank', 1000, 'IFRS', 'Reports in thousands SAR'),
(1140, 'Bank Albilad', 1000, 'IFRS', 'Reports in thousands SAR'),
(1150, 'Alinma Bank', 1000, 'IFRS', 'Reports in thousands SAR'),
(1180, 'The Saudi National Bank', 1000, 'IFRS', 'Reports in thousands SAR');

-- Major Industrial Companies
INSERT INTO company_unit_multipliers (ticker, company_name, unit_multiplier, reporting_standard, notes) VALUES
(2010, 'Saudi Basic Industries Corp. (SABIC)', 1000000, 'IFRS', 'Reports in millions SAR'),
(2020, 'SABIC Agri-Nutrients Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2030, 'Saudi Arabia Refineries Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2040, 'Saudi Ceramic Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2050, 'Savola Group', 1000, 'IFRS', 'Reports in thousands SAR'),
(2060, 'National Industrialization Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2070, 'Saudi Chemical Holding Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2080, 'National Gas and Industrialization Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2090, 'National Gypsum Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2100, 'Wafrah for Industry and Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2110, 'Saudi Cable Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2120, 'Saudi Advanced Industries Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2130, 'Saudi Industrial Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2140, 'Al Ahsa Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2150, 'Saudi Paper Manufacturing Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2160, 'Saudi Arabian Amiantit Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2170, 'Al Taiseer Group', 1000, 'IFRS', 'Reports in thousands SAR'),
(2180, 'Filing & Packing Materials Manufacturing Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2190, 'Saudi Industrial Services Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2200, 'Arabian Pipes Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2210, 'Nama Chemicals Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2220, 'National Metal Manufacturing and Casting Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2230, 'Petrochemical Conversion Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2240, 'Zamil Industrial Investment Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2250, 'Saudi Industrial Investment Group', 1000, 'IFRS', 'Reports in thousands SAR'),
(2260, 'Sahara International Petrochemical Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2270, 'Saudia Dairy and Foodstuff Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2280, 'Almarai Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2290, 'Yanbu National Petrochemical Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2300, 'Saudi Pharmaceutical Industries', 1000, 'IFRS', 'Reports in thousands SAR'),
(2310, 'Saudi Kayan Petrochemical Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2320, 'Alujain Corporation', 1000, 'IFRS', 'Reports in thousands SAR'),
(2330, 'Advanced Petrochemical Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2340, 'Al Babtain Power and Telecommunication Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2350, 'Saudi Electricity Co.', 1000000, 'IFRS', 'Reports in millions SAR'),
(2360, 'Saudi Vitrified Clay Pipes Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2370, 'Middle East Specialized Cables Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2380, 'Rabigh Refining and Petrochemical Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(2381, 'Saudi Aramco Total Refining', 1000, 'IFRS', 'Reports in thousands SAR'),
(2382, 'ACWA Power Co.', 1000, 'IFRS', 'Reports in thousands SAR');

-- Cement Companies
INSERT INTO company_unit_multipliers (ticker, company_name, unit_multiplier, reporting_standard, notes) VALUES
(3001, 'Hail Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3002, 'Najran Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3003, 'Northern Region Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3004, 'Umm Al-Qura Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3005, 'United Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3010, 'Arabian Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3020, 'Yamama Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3030, 'Saudi Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3040, 'Qassim Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3050, 'Southern Province Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3060, 'Yanbu Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3070, 'Eastern Province Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3080, 'Riyadh Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3090, 'Tabuk Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(3091, 'Al Jouf Cement Co.', 1000, 'IFRS', 'Reports in thousands SAR');

-- Insurance Companies
INSERT INTO company_unit_multipliers (ticker, company_name, unit_multiplier, reporting_standard, notes) VALUES
(8010, 'The Company for Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8012, 'Aljazira Takaful Taawuni Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8020, 'Malath Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8030, 'The Mediterranean and Gulf Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8040, 'Allianz Saudi Fransi Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8050, 'Salama Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8060, 'Walaa Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8070, 'Arabian Shield Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8100, 'Saudi Arabian Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8120, 'Gulf Union Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8150, 'Allied Cooperative Insurance Group', 1000, 'IFRS', 'Reports in thousands SAR'),
(8160, 'Arabia Insurance Cooperative Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8170, 'Al-Etihad Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8180, 'Al Sagr Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8190, 'United Cooperative Assurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8200, 'Saudi Re for Cooperative Reinsurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8230, 'Al-Rajhi Company for Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8240, 'CHUBB Arabia Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8250, 'AXA Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8260, 'Gulf General Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8280, 'Al Alamiya for Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR'),
(8300, 'Wataniya Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8310, 'Amana Cooperative Insurance Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(8311, 'Saudi Enaya Cooperative Insurance', 1000, 'IFRS', 'Reports in thousands SAR');

-- Retail and Services
INSERT INTO company_unit_multipliers (ticker, company_name, unit_multiplier, reporting_standard, notes) VALUES
(4001, 'Abdullah Al Othaim Markets Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4002, 'Mouwasat Medical Services Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4003, 'Extra Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4004, 'Dallah Healthcare Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4005, 'National Medical Care Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4007, 'Al Hammadi Development and Investment Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4008, 'Dr. Sulaiman Al Habib Medical Services', 1000, 'IFRS', 'Reports in thousands SAR'),
(4009, 'Middle East Healthcare Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4010, 'Saudi Transport and Investment Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4030, 'Saudi Ground Services Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4031, 'Saudi Airlines Catering Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4040, 'Saudi Public Transport Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4050, 'Saudi Automotive Services Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4051, 'Bahri', 1000, 'IFRS', 'Reports in thousands SAR'),
(4061, 'Anaam International Holding Group', 1000, 'IFRS', 'Reports in thousands SAR'),
(4070, 'Tihama Advertising Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4071, 'MBC Group Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4072, 'MBC Group Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4080, 'Ash-Sharqiyah Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4090, 'Taiba Holding Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4100, 'Makkah Construction and Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4110, 'Saudi Hotels and Resort Areas Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4130, 'Al Baha Development and Investment Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4140, 'Saudi Real Estate Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4150, 'Arriyadh Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4160, 'Thimar Development Holding Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4161, 'Bin Dawood Holding Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4162, 'Jadwa REIT Saudi Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4163, 'Retal Urban Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4164, 'Nahdi Medical Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4170, 'Tourism Enterprise Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4180, 'Dur Hospitality Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4190, 'Jarir Marketing Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4191, 'Abdullah Saad Mohammed Abo Moati for Bookstores', 1000, 'IFRS', 'Reports in thousands SAR'),
(4200, 'Aldrees Petroleum and Transport', 1000, 'IFRS', 'Reports in thousands SAR'),
(4210, 'Saudi Research and Media Group', 1000, 'IFRS', 'Reports in thousands SAR'),
(4220, 'Emaar The Economic City', 1000, 'IFRS', 'Reports in thousands SAR'),
(4230, 'Red Sea International Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4240, 'Fawaz Abdulaziz Alhokair Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4250, 'Jabal Omar Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4260, 'Budget Saudi Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4261, 'Theeb Rent a Car Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4270, 'Knowledge Economic City', 1000, 'IFRS', 'Reports in thousands SAR'),
(4280, 'Kingdom Holding Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4290, 'Alkhaleej Training and Education Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4291, 'National Company for Learning and Education', 1000, 'IFRS', 'Reports in thousands SAR'),
(4292, 'Ataa Educational Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4300, 'Dar Al Arkan Real Estate Development Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4310, 'Knowledge Towers Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4320, 'Al Andalus Property Co.', 1000, 'IFRS', 'Reports in thousands SAR'),
(4321, 'Riyad REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4322, 'Jadwa REIT Al Haramain Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4330, 'SEDCO Capital REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4331, 'Al Maather REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4332, 'Jadwa REIT Saudi Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4333, 'Taleem REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4334, 'Mefic REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4335, 'Musharaka REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4336, 'Mulkia Gulf REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4337, 'Alahli REIT Fund (1)', 1000, 'IFRS', 'Reports in thousands SAR'),
(4338, 'Alrajhi REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4339, 'Derayah REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4340, 'Alinma Retail REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4342, 'Swicorp Wabel REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4344, 'Saudi Fransi Capital Hospitality REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4345, 'Bonyan REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4346, 'Al-Bilad Logistic REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR'),
(4347, 'Al-Jazira Mawten REIT', 1000, 'IFRS', 'Reports in thousands SAR'),
(4348, 'Al-Istithmar REIT Fund', 1000, 'IFRS', 'Reports in thousands SAR');

-- ============================================================================
-- SECTION 2: CREATE/UPDATE sector_classifications TABLE
-- ============================================================================

DROP TABLE IF EXISTS sector_classifications;

CREATE TABLE sector_classifications (
    ticker INT PRIMARY KEY,
    company_name VARCHAR(255),
    gics_sector VARCHAR(100),
    gics_industry_group VARCHAR(100),
    gics_industry VARCHAR(100),
    company_category VARCHAR(50),
    is_financial_institution BOOLEAN DEFAULT FALSE,
    is_bank BOOLEAN DEFAULT FALSE,
    is_insurance BOOLEAN DEFAULT FALSE,
    requires_special_metrics BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- Banks
INSERT INTO sector_classifications (ticker, company_name, gics_sector, gics_industry_group, gics_industry, company_category, is_financial_institution, is_bank, requires_special_metrics) VALUES
(1010, 'Riyad Bank', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1020, 'Bank Aljazira', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1030, 'Saudi Investment Bank', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1050, 'Banque Saudi Fransi', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1060, 'Saudi Awwal Bank', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1080, 'Arab National Bank', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1120, 'Al Rajhi Bank', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1140, 'Bank Albilad', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1150, 'Alinma Bank', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE),
(1180, 'The Saudi National Bank', 'Financials', 'Banks', 'Banks', 'Bank', TRUE, TRUE, TRUE);

-- Insurance Companies
INSERT INTO sector_classifications (ticker, company_name, gics_sector, gics_industry_group, gics_industry, company_category, is_financial_institution, is_insurance, requires_special_metrics) VALUES
(8010, 'The Company for Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8012, 'Aljazira Takaful Taawuni Co.', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8020, 'Malath Cooperative Insurance Co.', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8030, 'Med & Gulf Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8040, 'Allianz Saudi Fransi Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8050, 'Salama Cooperative Insurance Co.', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8060, 'Walaa Cooperative Insurance Co.', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8070, 'Arabian Shield Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8100, 'Saudi Arabian Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8120, 'Gulf Union Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8150, 'Allied Cooperative Insurance Group', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8160, 'Arabia Insurance Cooperative Co.', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8170, 'Al-Etihad Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8180, 'Al Sagr Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8190, 'United Cooperative Assurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8200, 'Saudi Re for Cooperative Reinsurance', 'Financials', 'Insurance', 'Reinsurance', 'Reinsurance', TRUE, TRUE, TRUE),
(8230, 'Al-Rajhi Company for Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8240, 'CHUBB Arabia Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8250, 'AXA Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8260, 'Gulf General Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8280, 'Al Alamiya for Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8300, 'Wataniya Insurance Co.', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8310, 'Amana Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE),
(8311, 'Saudi Enaya Cooperative Insurance', 'Financials', 'Insurance', 'Insurance', 'Insurance', TRUE, TRUE, TRUE);

-- Finance Companies (Non-Bank)
INSERT INTO sector_classifications (ticker, company_name, gics_sector, gics_industry_group, gics_industry, company_category, is_financial_institution, requires_special_metrics) VALUES
(1182, 'Amlak International Finance Co.', 'Financials', 'Diversified Financials', 'Consumer Finance', 'Finance', TRUE, TRUE),
(1183, 'Saudi Home Loans Co.', 'Financials', 'Diversified Financials', 'Consumer Finance', 'Finance', TRUE, TRUE);

-- Major Industrial Companies
INSERT INTO sector_classifications (ticker, company_name, gics_sector, gics_industry_group, gics_industry, company_category) VALUES
(2010, 'Saudi Basic Industries Corp. (SABIC)', 'Materials', 'Materials', 'Chemicals', 'Petrochemicals'),
(2020, 'SABIC Agri-Nutrients Co.', 'Materials', 'Materials', 'Chemicals', 'Fertilizers'),
(2030, 'Saudi Arabia Refineries Co.', 'Energy', 'Energy', 'Oil, Gas & Consumable Fuels', 'Refining'),
(2050, 'Savola Group', 'Consumer Staples', 'Food & Staples Retailing', 'Food & Staples Retailing', 'Food'),
(2060, 'National Industrialization Co.', 'Materials', 'Materials', 'Chemicals', 'Industrial'),
(2070, 'Saudi Chemical Holding', 'Materials', 'Materials', 'Chemicals', 'Chemicals'),
(2080, 'National Gas and Industrialization', 'Materials', 'Materials', 'Chemicals', 'Industrial Gas'),
(2090, 'National Gypsum Co.', 'Materials', 'Materials', 'Construction Materials', 'Building Materials'),
(2110, 'Saudi Cable Co.', 'Industrials', 'Capital Goods', 'Electrical Equipment', 'Cables'),
(2150, 'Saudi Paper Manufacturing', 'Materials', 'Materials', 'Paper & Forest Products', 'Paper'),
(2170, 'Al Taiseer Group', 'Consumer Discretionary', 'Consumer Durables & Apparel', 'Household Durables', 'Industrial'),
(2190, 'Saudi Industrial Services', 'Industrials', 'Capital Goods', 'Industrial Conglomerates', 'Industrial'),
(2200, 'Arabian Pipes Co.', 'Materials', 'Materials', 'Metals & Mining', 'Pipes'),
(2210, 'Nama Chemicals', 'Materials', 'Materials', 'Chemicals', 'Chemicals'),
(2220, 'National Metal Manufacturing', 'Materials', 'Materials', 'Metals & Mining', 'Metals'),
(2240, 'Zamil Industrial Investment', 'Industrials', 'Capital Goods', 'Industrial Conglomerates', 'Industrial'),
(2250, 'Saudi Industrial Investment Group', 'Materials', 'Materials', 'Chemicals', 'Industrial'),
(2260, 'Sahara International Petrochemical', 'Materials', 'Materials', 'Chemicals', 'Petrochemicals'),
(2270, 'Saudia Dairy and Foodstuff', 'Consumer Staples', 'Food, Beverage & Tobacco', 'Food Products', 'Food'),
(2280, 'Almarai Co.', 'Consumer Staples', 'Food, Beverage & Tobacco', 'Food Products', 'Dairy'),
(2290, 'Yanbu National Petrochemical', 'Materials', 'Materials', 'Chemicals', 'Petrochemicals'),
(2300, 'Saudi Pharmaceutical Industries', 'Health Care', 'Pharmaceuticals, Biotechnology & Life Sciences', 'Pharmaceuticals', 'Pharma'),
(2310, 'Saudi Kayan Petrochemical', 'Materials', 'Materials', 'Chemicals', 'Petrochemicals'),
(2320, 'Alujain Corporation', 'Materials', 'Materials', 'Chemicals', 'Petrochemicals'),
(2330, 'Advanced Petrochemical', 'Materials', 'Materials', 'Chemicals', 'Petrochemicals'),
(2340, 'Al Babtain Power and Telecom', 'Industrials', 'Capital Goods', 'Electrical Equipment', 'Power'),
(2350, 'Saudi Electricity Co.', 'Utilities', 'Utilities', 'Electric Utilities', 'Utility'),
(2380, 'Rabigh Refining and Petrochemical', 'Energy', 'Energy', 'Oil, Gas & Consumable Fuels', 'Refining'),
(2382, 'ACWA Power Co.', 'Utilities', 'Utilities', 'Independent Power Producers', 'Power');

-- Cement Companies
INSERT INTO sector_classifications (ticker, company_name, gics_sector, gics_industry_group, gics_industry, company_category) VALUES
(3001, 'Hail Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3002, 'Najran Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3003, 'Northern Region Cement', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3004, 'Umm Al-Qura Cement', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3010, 'Arabian Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3020, 'Yamama Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3030, 'Saudi Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3040, 'Qassim Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3050, 'Southern Province Cement', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3060, 'Yanbu Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3070, 'Eastern Province Cement', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3080, 'Riyadh Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3090, 'Tabuk Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement'),
(3091, 'Al Jouf Cement Co.', 'Materials', 'Materials', 'Construction Materials', 'Cement');

-- ============================================================================
-- SECTION 3: CREATE data_quality_flags TABLE
-- ============================================================================

DROP TABLE IF EXISTS data_quality_flags;

CREATE TABLE data_quality_flags (
    id SERIAL PRIMARY KEY,
    ticker INT,
    fiscal_year INT,
    period_type VARCHAR(20),
    flag_type VARCHAR(50),
    flag_description TEXT,
    severity VARCHAR(20), -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    resolution_status VARCHAR(20) DEFAULT 'OPEN', -- 'OPEN', 'IN_PROGRESS', 'RESOLVED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    notes TEXT
);

-- Flag missing 2024 annual data for major companies
INSERT INTO data_quality_flags (ticker, fiscal_year, period_type, flag_type, flag_description, severity) VALUES
-- Banks
(1050, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'CRITICAL'),
(1080, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'CRITICAL'),
(1120, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data - Major bank', 'CRITICAL'),
(1180, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data - Largest bank', 'CRITICAL'),

-- Major Industrial
(2010, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data - SABIC (largest non-oil company)', 'CRITICAL'),
(2020, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data - SABIC Agri', 'HIGH'),
(2080, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'HIGH'),
(1320, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'MEDIUM'),

-- Insurance Companies
(8010, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'HIGH'),
(8020, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'HIGH'),
(8030, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'HIGH'),
(8040, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'MEDIUM'),
(8050, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'MEDIUM'),
(8060, 2024, 'Annual', 'MISSING_DATA', 'Missing 2024 annual financial data', 'MEDIUM');

-- Flag companies with NULL revenue that shouldn't have NULL
INSERT INTO data_quality_flags (ticker, fiscal_year, period_type, flag_type, flag_description, severity)
SELECT DISTINCT
    ticker,
    2024,
    'Annual',
    'NULL_REVENUE',
    'Revenue is NULL - needs data sourcing (non-financial company)',
    'HIGH'
FROM (
    VALUES
    (1210), (1320), (1323), (1820), (1831),
    (2010), (2020), (2030), (2040), (2240),
    (2270), (2280), (2370), (3002), (3008),
    (3090), (3091), (4001), (4004), (4050),
    (4070), (4072), (4130), (4164), (4170),
    (4191), (4200), (4220), (4230), (4240),
    (4261), (4265), (4280), (4292)
) AS t(ticker);

-- Flag banks/insurance for special metric requirements
INSERT INTO data_quality_flags (ticker, fiscal_year, period_type, flag_type, flag_description, severity, notes) VALUES
(1010, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1020, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1030, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1050, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1060, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1080, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1120, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1140, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1150, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations'),
(1180, NULL, NULL, 'SPECIAL_METRICS', 'Bank - requires Net Interest Income instead of Revenue', 'LOW', 'Use bank_metrics.py for proper calculations');

-- Flag low data quality scores
INSERT INTO data_quality_flags (ticker, fiscal_year, period_type, flag_type, flag_description, severity)
SELECT DISTINCT
    ticker,
    NULL,
    NULL,
    'LOW_QUALITY_SCORE',
    'Data quality score below 20 - needs comprehensive review',
    'HIGH'
FROM (
    VALUES
    (4240), (1080), (1140), (1050), (1182),
    (1020), (1120), (1183), (1060), (1030),
    (1180), (1150), (1010), (4072)
) AS t(ticker);

-- ============================================================================
-- SECTION 4: UPDATE QUERIES FOR EXISTING TABLES
-- ============================================================================

-- Update sector_gics in main financials table (if it exists as a table)
-- This assumes TASI_financials_DB can be imported as a table

-- Create view for easy querying of missing data
CREATE OR REPLACE VIEW v_missing_2024_annual AS
SELECT DISTINCT
    f.ticker,
    f.company_name,
    COALESCE(s.gics_sector, 'Unknown') as sector,
    COALESCE(s.company_category, 'Unknown') as category,
    s.is_bank,
    s.is_insurance,
    s.requires_special_metrics
FROM company_unit_multipliers f
LEFT JOIN sector_classifications s ON f.ticker = s.ticker
WHERE f.ticker NOT IN (
    SELECT DISTINCT ticker
    FROM data_quality_flags
    WHERE fiscal_year = 2024
    AND period_type = 'Annual'
    AND flag_type = 'MISSING_DATA'
    AND resolution_status = 'RESOLVED'
);

-- Create view for companies needing special metrics
CREATE OR REPLACE VIEW v_special_metrics_companies AS
SELECT
    s.ticker,
    s.company_name,
    s.gics_sector,
    s.company_category,
    CASE
        WHEN s.is_bank THEN 'BANK'
        WHEN s.is_insurance THEN 'INSURANCE'
        ELSE 'FINANCE'
    END as institution_type,
    'Net Interest Income/Gross Written Premiums instead of Revenue' as metric_note
FROM sector_classifications s
WHERE s.requires_special_metrics = TRUE;

-- ============================================================================
-- SECTION 5: UTILITY PROCEDURES
-- ============================================================================

-- Procedure to mark a data quality flag as resolved
CREATE OR REPLACE PROCEDURE resolve_data_quality_flag(
    p_ticker INT,
    p_fiscal_year INT,
    p_flag_type VARCHAR(50),
    p_notes TEXT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE data_quality_flags
    SET
        resolution_status = 'RESOLVED',
        resolved_at = CURRENT_TIMESTAMP,
        notes = COALESCE(p_notes, notes)
    WHERE ticker = p_ticker
    AND (fiscal_year = p_fiscal_year OR (fiscal_year IS NULL AND p_fiscal_year IS NULL))
    AND flag_type = p_flag_type;
END;
$$;

-- Procedure to add new data quality flag
CREATE OR REPLACE PROCEDURE add_data_quality_flag(
    p_ticker INT,
    p_fiscal_year INT,
    p_period_type VARCHAR(20),
    p_flag_type VARCHAR(50),
    p_description TEXT,
    p_severity VARCHAR(20)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO data_quality_flags (ticker, fiscal_year, period_type, flag_type, flag_description, severity)
    VALUES (p_ticker, p_fiscal_year, p_period_type, p_flag_type, p_description, p_severity);
END;
$$;

-- ============================================================================
-- SUMMARY QUERIES
-- ============================================================================

-- Query to get summary of data quality issues
-- SELECT flag_type, severity, COUNT(*) as count
-- FROM data_quality_flags
-- WHERE resolution_status = 'OPEN'
-- GROUP BY flag_type, severity
-- ORDER BY
--     CASE severity
--         WHEN 'CRITICAL' THEN 1
--         WHEN 'HIGH' THEN 2
--         WHEN 'MEDIUM' THEN 3
--         WHEN 'LOW' THEN 4
--     END;

-- Query to list all open critical issues
-- SELECT ticker, fiscal_year, flag_description
-- FROM data_quality_flags
-- WHERE severity = 'CRITICAL' AND resolution_status = 'OPEN'
-- ORDER BY ticker;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
