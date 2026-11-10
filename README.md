# ⚡ AI Algorithmic Scalper Engine

An enterprise-grade, fully automated 1-minute stock scalping engine engineered with Python, local LLMs, and microservice orchestration. Built for high-frequency US equity execution with dynamic risk evaluation, real-time market data ingestion, and micro-budget compute efficiency.

---

## 🌟 Key Features

* **Local Multi-Agent AI Strategy:** Leverages local Ollama LLMs (Qwen3) as autonomous market analysts and risk orchestrators for sub-second trade decisions.
* **Deterministic Risk Engine:** Dynamically calculates position sizing, dynamic stop-loss, and take-profit targets via ATR, RSI (14), and dual EMA (9/21) indicators.
* **Alpaca API Trading Engine:** Executes live US market equities paper/live orders with instant account synchronization and equity management.
* **Smart Market Kill-Switch:** Embedded Python guardrails (`clock.is_open`) eliminate zero-value API processing and compute usage outside US market hours.
* **Automated Workflow Scheduling:** n8n orchestration triggers precise 1-minute evaluation pipelines with complete fault isolation.
* **Persisted Signal Telemetry:** PostgreSQL data pipeline records complete indicator states, LLM rationale, and trade execution logs for post-trade analysis.
* **Production Containerization:** Fully dockerized stack (`docker-compose.yml`) deploying PostgreSQL 16 Alpine and n8n with health-check dependency mapping.

---

## 🏗 System Architecture


  [ n8n Scheduler ] ──(Every 1-Min)──> [ FastAPI Endpoint ]
                                              │
                                              ▼
                                   [ US Market Clock Check ]
                                              │ (If Open)
                                              ▼
    [ Alpaca Market Data ] ──> [ Technical Indicators (EMA/RSI/ATR) ]
                                              │
                                              ▼
                                     [ Local Ollama Agent ]
                                              │
                                              ▼
      [ PostgreSQL DB ] <──(Log Signal)── [ Alpaca Execution ]

---

## ***Quick Start (Local Setup)***

# **Clone repository & prepare environment:**

git clone https://github.com/Akyy03/ai-stock-trader.git
cd ai-stock-trader
cp .env.example .env

# **Spin up Docker infrastructure:**

docker-compose up -d

# **Install dependencies & run API server:**

python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python api.py

# **Security & Credentials**

All API secrets, database passwords, and private environment details are strictly isolated in local .env configuration files and excluded from repository index tracking via .gitignore.
