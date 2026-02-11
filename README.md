# 🛢️ CL Option Zone Analyzer

**Automated Volume Profile & Strategy Engine for Crude Oil (CL)**

A quantitative analysis tool designed to identify high-probability trading zones for WTI Crude Oil Futures (CL) using **Volume Profile** metrics. It automatically calculates key support/resistance levels and suggests optimal option strategies based on market context.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)

## 🎯 Core Features

- **Volume Profile Analysis**:
  - **POC (Point of Control)**: The price level with the highest traded volume (Magnet).
  - **VAH / VAL**: Value Area High/Low (70% volume range).
  - **HVN (High Volume Nodes)**: Strong support/resistance zones.
  - **LVN (Low Volume Nodes)**: Fast-move "vacuum" zones.

- **Automated Strategy Context**:
  - Detects if price is **In-Balance** (Range-bound) or **Imbalanced** (Trend).
  - Suggests **Mean Reversion** vs **Breakout** strategies.

- **Data Source**:
  - Uses `yfinance` (CL=F) for free, delayed data (perfect for daily analysis).
  - Modular design allows easy swap to IBKR/TickData.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/hi66724389/cl-option-zone.git
cd cl-option-zone

# Install dependencies
pip install -r requirements.txt
```

### 2. Usage

Run the analyzer with default settings (5-day lookback, 150 bins):

```bash
python main.py
```

**Custom Settings:**

```bash
# Analyze last 10 days with higher resolution
python main.py --period 10d --bins 200

# Analyze a different ticker (e.g., GC=F for Gold)
python main.py --symbol GC=F
```

## 📊 Output Example

```text
📊 CL Option Zone Analyzer
Target: CL=F | Period: 5d

✅ Data loaded: 1440 candles. Last Price: 76.54

🛡️ Key Levels & Zones
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Metric               ┃ Price Level ┃ Relation to Spot ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Current Price        │       76.54 │ -                │
│ VAH (Value Area High)│       77.20 │ +0.66            │
│ POC (Point of Control│       76.10 │ -0.44            │
│ VAL (Value Area Low) │       75.80 │ -0.74            │
└──────────────────────┴─────────────┴──────────────────┘

🧠 AI Strategy Assistant
Market Context: INSIDE VALUE

🎯 Trading Plan:
• POC (76.10): Magnet. Expect reversion here.
• VAH (77.20): Resistance. Look for shorts if price rejects.
• VAL (75.80): Support. Look for longs if price reclaims.

⚠️ High Volume Nodes (Support/Resistance):
76.10, 75.50, 77.00

🚀 Low Volume Nodes (Fast Zones):
76.80, 75.20
```

## 🧠 Theory & Logic

### Volume Profile
The script constructs a histogram of volume at price over the specified period (`--period`).
- **Value Area (70%)**: Where 70% of all trading occurred. Smart money consensus.
- **POC**: The "fairest" price. Price tends to revert here.

### Option Strategy Mapping
- **Inside Value**: Market is balanced. Prefer **Iron Condors** or **Credit Spreads** (Short Vega/Theta).
- **Outside Value**: Market is imbalanced. Prefer **Directional Spreads** or **Long Options** (Long Gamma).

## ⚠️ Disclaimer

This software is for **educational and research purposes only**. It does not constitute financial advice. Futures and options trading involves substantial risk of loss.

---

**Author**: hi66724389
**License**: MIT
