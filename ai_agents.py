import requests
import os

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434/api/generate")
MODEL_NAME = "qwen3:4b-instruct"

def query_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Ollama exception: {e}"

def market_analyst_agent(symbol: str, tech_summary: dict) -> str:
    prompt = f"""You are a senior Market Analyst.
Analyze the following technical indicators for {symbol} on a 1-minute chart:
- Current Price: 
- EMA 9: {tech_summary.get('ema_9')}
- EMA 21: {tech_summary.get('ema_21')}
- RSI (14): {tech_summary.get('rsi')}
- ATR (14): {tech_summary.get('atr')}

Provide a concise technical summary (2-3 sentences) covering:
1. Trend structure (bullish, bearish, or flat).
2. Momentum (RSI).
3. Volatility and buying/selling pressure.
Be factual, professional, and objective.
"""
    return query_ollama(prompt)

def strategy_agent(symbol: str, analyst_summary: str, risk_decision: dict) -> str:
    signal = risk_decision.get('signal', 'HOLD')
    reason = risk_decision.get('reason', 'N/A')
    entry_price = risk_decision.get('entry_price', 0.0)

    prompt = f"""You are the Chief Investment Officer & Risk Manager.
Review the analysis and proposed risk parameters for {symbol}:

Market Analyst Report:
{analyst_summary}

Deterministic Risk Engine Decision:
- Proposed Signal: {signal}
- Reason: {reason}
- Reference Price: 

Your task:
Evaluate if the Risk Engine decision aligns with the Market Analyst context.
If the signal is BUY or SELL, validate it. If it is HOLD, confirm why holding is prudent.

Output format:
Executive Summary: (2 sentences)
Final Recommendation: [CONFIRM {signal}] or [REJECT]
Rationale: (2 sentences)
"""
    return query_ollama(prompt)
