# 🏭 Supply Chain Inventory Simulation
### Agent-Based Model with Mesa — Foundation for LLM Agentic Workflow

## 📌 Overview

This project implements a **supply chain inventory simulation** using **Agent-Based Modeling (ABM)** with the [Mesa](https://mesa.readthedocs.io/) library.


## 🤖 Agents

| Agent | Role |
|---|---|
| `CustomerAgent` | Generates stochastic daily demand (Gaussian distribution) |
| `RetailerAgent` | Manages inventory using **(s, S)** reorder-point policy |
| `SupplierAgent` | Fills orders subject to daily capacity constraints |

---

## 📊 What it simulates

- **90-day** inventory dynamics
- **Reorder point policy** — orders when inventory drops below `s`, orders up to `S`
- **Lead time delays** — supplier delivers after `n` days
- **KPI tracking** — inventory level, backlog, holding cost, backlog cost, service level
- **Scenario comparison** — Baseline vs. Supply Disruption (longer lead time) vs. Capacity Shock

---

## 🚀 Quick Start

### Option 1 — Google Colab (recommended)
Click the badge above, or open `supply_chain_simulation.ipynb` directly in Colab. Run cells top to bottom.

### Option 2 — Local
```bash
git clone https://github.com/MuhammedOzluDev/mesa-supply-chain-simulation.git
cd mesa-supply-chain-simulation
pip install -r requirements.txt
python run_simulation.py
```

---

## 📁 Project Structure

```
mesa-supply-chain-simulation/
│
├── simulation.py                  # Agent & Model definitions
├── run_simulation.py              # Run script + charts + scenario comparison
├── supply_chain_simulation.ipynb  # Google Colab notebook (all-in-one)
├── requirements.txt
├── outputs/                       # Charts and CSV saved here
└── README.md
```

---

## 📈 Sample Output

**Baseline scenario (s=40, S=120, Lead Time=3 days):**

| Metric | Value |
|---|---|
| Avg Daily Inventory | ~72 units |
| Service Level | ~94% |
| Days with Stockout | ~5 days |

---

## 🔮 Next Step — LLM Agent Integration

The `RetailerAgent` currently uses a hard-coded **(s, S)** rule. The next phase replaces this with an **LLM-powered agentic workflow**:

```python
# Planned extension
prompt = f"""
Current inventory: {self.inventory} units
Backlog: {self.backlog} units
Lead time: {self.lead_time} days
Recent demand trend: {recent_demand}

Should I place an order today? If yes, how many units?
Think step by step.
"""
decision = llm.invoke(prompt)  # Chain-of-Thought reasoning
```

This enables:
- 🗣️ **Natural language** managerial goal-setting
- 🧠 **Contextual reasoning** under disruption scenarios
- 📋 **Explainable** inventory decisions
- 🔗 **RAG integration** for real-time market data

---

## 👤 Author

**Muhammed Özlü** — Management Information Systems, İzmir Bakırçay University  
Erasmus+ Exchange Student @ Vilnius University (2026)
