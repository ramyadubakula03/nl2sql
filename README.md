# NL2SQL — Natural Language to SQL Query Engine

Ask questions in plain English, get SQL + results instantly. Powered by Claude AI with a rule-based fallback.

## Features

| Feature | Description |
|---|---|
| **AI-Powered** | Uses Claude API to generate accurate SQL from natural language |
| **Rule-Based Fallback** | Works without API key using pattern matching |
| **Schema-Aware** | Prompts include full table schema for accurate queries |
| **Live Execution** | Generated SQL runs against a real SQLite database |
| **Query History** | Every question and result is saved for review |
| **Schema Explorer** | Browse all tables and columns in the UI |
| **Syntax Highlighting** | SQL displayed with keyword highlighting |

## Project Structure

```
nl2sql/
├── app.py              # Flask API + Web Dashboard
├── requirements.txt
├── data/
│   └── analytics.db    # SQLite database (auto-created)
└── core/
    ├── database.py     # Schema, sample data, query executor
    └── engine.py       # NL → SQL engine (Claude + fallback)
```

## Quick Start

```bash
pip install flask requests
python app.py
# Visit http://localhost:5002
```

## With Claude AI (recommended)

```bash
set ANTHROPIC_API_KEY=your_key_here
python app.py
```

Get your API key at: https://console.anthropic.com

## Sample Questions

- "What is the average salary by department?"
- "Show the top 5 highest paid employees"
- "Total revenue by product for delivered orders"
- "How many employees are in each department?"
- "Which products have low stock?"
- "Show all pending orders"

## Tech Stack
Python 3, Flask, SQLite, Claude API (Anthropic), requests
Production path: Azure OpenAI, Azure SQL, Microsoft Fabric, Power BI
