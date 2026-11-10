## **AI Algorithmic Trading Engine**
An enterprise-grade, fully automated multi-asset algorithmic trading engine engineered with Python, local LLMs, and native task scheduling. Built for high-frequency execution across stocks and cryptocurrencies with dynamic risk evaluation, real-time market data ingestion, and micro-budget compute efficiency.

---

## **Key Features**
- Local Multi-Agent AI Strategy: Leverages local Ollama LLMs as autonomous market analysts and risk orchestrators for real-time trade decisions.

- Deterministic Risk Engine: Dynamically calculates position sizing, dynamic stop-loss, and take-profit targets via technical indicators like ATR, RSI (14), and dual EMAs.

- Multi-Asset Execution Pipeline: Executes automated trades across multiple asset classes (stocks and cryptocurrencies) with instant account synchronization and equity management.

- Native Task Orchestration: Powered by a built-in Python APScheduler pipeline for autonomous trade evaluations with complete fault isolation, replacing external workflow dependencies.

- Smart Market Guardrails: Embedded backend scheduling checks eliminate redundant API processing and optimize compute usage outside active trading windows.

- Persisted Signal Telemetry: PostgreSQL data pipeline records complete indicator states, LLM rationale, and trade execution logs for post-trade analysis.

- Angular Real-Time Dashboard: Fully interactive frontend interface featuring live telemetry polling, manual overrides, and a system Auto-Mode toggle.

- Production Containerization: Fully dockerized stack deploying PostgreSQL and the backend with health-check dependency mapping.

---

## **Quick Start (Local Setup)**
To get the application up and running locally, clone the repository, configure your environment variables, and initialize the system services:

# **Clone repository & prepare environment:**
git clone https://github.com/Akyy03/ai-stock-trader.git
cd ai-stock-trader
cp .env.example .env

# **Spin up Docker infrastructure:**
docker compose up -d

# **Install dependencies & run API server:**
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py

---

## Security & Credentials
All API secrets, database passwords, and private environment details are strictly isolated in local configuration files and excluded from repository index tracking.
