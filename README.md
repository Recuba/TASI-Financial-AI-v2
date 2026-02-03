# Venna AI - TASI Financial Analytics Platform

A powerful natural language interface for querying Saudi Stock Exchange (TASI) financial data. Ask questions in plain English and get instant insights powered by AI.

![Venna AI](https://img.shields.io/badge/Venna%20AI-TASI%20Analytics-006C35?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## Features

- **Natural Language Queries**: Ask questions like "Show me the top 10 most profitable companies" or "Compare sector performance by ROE"
- **AI-Powered SQL Generation**: Converts natural language to optimized PostgreSQL queries using Gemini Flash 2.5
- **Real-Time Financial Data**: Access comprehensive TASI financial metrics including:
  - Revenue, Net Profit, Assets, Equity
  - ROE, Net Margin, Current Ratio, Debt-to-Equity
  - Sector classifications and performance categories
- **Interactive Data Tables**: View, sort, and filter results with ease
- **Export Functionality**: Download results as CSV or Excel files
- **Saudi-Themed UI**: Beautiful dark theme with Saudi green and gold branding

## Screenshots

<!-- Add screenshots here -->
![Dashboard Preview](screenshots/dashboard.png)
*Main dashboard with natural language query interface*

![Query Results](screenshots/results.png)
*Example query results with data visualization*

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database with TASI financial data
- OpenRouter API key (for AI features)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TASI-Financial-AI-v2.git
   cd TASI-Financial-AI-v2
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and API keys
   ```

5. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:8501`

## Database Setup

### Option 1: Local PostgreSQL

1. Install PostgreSQL
2. Create a database:
   ```sql
   CREATE DATABASE tasi_financials;
   CREATE USER tasi WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE tasi_financials TO tasi;
   ```
3. Run the schema setup:
   ```bash
   python setup_database.py
   ```
4. Migrate the data:
   ```bash
   python migrate_data.py
   ```

### Option 2: Cloud PostgreSQL (Recommended for Production)

We recommend [Neon](https://neon.tech) for serverless PostgreSQL:

1. Create a free Neon account
2. Create a new project and database
3. Copy your connection string
4. Use the connection string in your environment variables

## Deployment to Streamlit Cloud

### Step 1: Prepare Your Repository

Ensure your repository has:
- `streamlit_app.py` (entry point)
- `requirements.txt`
- `.streamlit/config.toml`

### Step 2: Set Up Cloud Database

1. Create a [Neon](https://neon.tech) PostgreSQL database
2. Run the schema and data migration scripts against your cloud database
3. Note your connection string

### Step 3: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Select `streamlit_app.py` as the main file
4. Add secrets in the Streamlit Cloud dashboard:

```toml
[database]
url = "postgresql://user:password@ep-xxx.region.aws.neon.tech/tasi_financials?sslmode=require"

[openrouter]
api_key = "sk-or-v1-your-api-key"
```

5. Click Deploy!

### Step 4: Verify Deployment

- Check the app loads correctly
- Verify database connection (green status in sidebar)
- Test a sample query

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM | Yes |
| `VANNA_API_KEY` | Vanna.ai API key (optional) | No |

### Streamlit Secrets

For Streamlit Cloud deployment, configure secrets in the dashboard:

```toml
[database]
url = "your-database-url"

[openrouter]
api_key = "your-api-key"
```

## Project Structure

```
venna-ai/
├── streamlit_app.py      # Main Streamlit application
├── vanna_app.py          # AI agent and SQL generation
├── requirements.txt      # Python dependencies
├── components/           # UI components
│   ├── __init__.py
│   ├── chat.py          # Chat interface
│   ├── sidebar.py       # Sidebar controls
│   └── example_questions.py
├── styles/              # CSS styling
│   ├── __init__.py
│   ├── variables.py     # Design tokens
│   └── css.py           # CSS generation
├── schema/              # Database schema
│   ├── 01_schema.sql    # Table definitions
│   └── ...
├── .streamlit/          # Streamlit configuration
│   ├── config.toml
│   └── secrets.toml.example
└── data/                # Data files
```

## Example Queries

Try these natural language queries:

- "Show me the top 10 most profitable companies"
- "Which companies have the highest ROE?"
- "Compare sector performance by average revenue"
- "Show companies with losses in the insurance sector"
- "What is the total revenue by sector?"
- "List companies with high debt-to-equity ratio"
- "Show year-over-year financial summary"

## Tech Stack

- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **AI/LLM**: Gemini Flash 2.5 via OpenRouter
- **Styling**: Custom CSS with Saudi green/gold theme
- **Data Processing**: Pandas, NumPy

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Saudi Stock Exchange (TASI) for financial data
- OpenRouter for AI API access
- Streamlit for the amazing web framework
- Neon for serverless PostgreSQL

---

**Built with love for the Saudi financial community**
