"""
run_simulation.py
-----------------
Runs the supply chain simulation and produces charts + a summary table.
Works in:
  - Local Python  →  python run_simulation.py
  - Google Colab  →  run each cell marked with  # ── CELL
  - GitHub        →  results saved to /outputs/
"""

# ── CELL 1: Install dependencies (Colab only – skip if running locally)
# !pip install mesa matplotlib pandas -q

# ── CELL 2: Imports
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from simulation import SupplyChainModel

os.makedirs("outputs", exist_ok=True)

# ── CELL 3: Run baseline simulation
print("=" * 55)
print("  SUPPLY CHAIN INVENTORY SIMULATION  (Mesa ABM)")
print("=" * 55)

model = SupplyChainModel(
    n_customers=5,
    mean_demand=20,
    std_demand=5,
    reorder_point=40,
    order_up_to=120,
    lead_time=3,
    supplier_cap=150,
    seed=42
)

df = model.run(steps=90)
df.index.name = "Day"
print(f"\n✅ Simulation complete — {len(df)} days simulated.\n")

# ── CELL 4: Summary statistics
summary = pd.DataFrame({
    "Metric": [
        "Avg Daily Inventory",
        "Avg Daily Backlog",
        "Total Holding Cost",
        "Total Backlog Cost",
        "Total Cost",
        "Days with Stockout",
        "Service Level (%)",
    ],
    "Value": [
        f"{df['Inventory'].mean():.1f}",
        f"{df['Backlog'].mean():.1f}",
        f"${df['HoldingCost'].iloc[-1]:,.0f}",
        f"${df['BacklogCost'].iloc[-1]:,.0f}",
        f"${df['HoldingCost'].iloc[-1] + df['BacklogCost'].iloc[-1]:,.0f}",
        f"{(df['Backlog'] > 0).sum()} days",
        f"{100 * (1 - (df['Backlog'] > 0).mean()):.1f}%",
    ]
})
print(summary.to_string(index=False))
summary.to_csv("outputs/summary.csv", index=False)

# ── CELL 5: Plot
fig = plt.figure(figsize=(14, 10))
fig.suptitle("Supply Chain Simulation — Baseline (s=40, S=120, LT=3 days)",
             fontsize=14, fontweight="bold", y=1.01)

gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

# 1. Inventory level
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(df.index, df["Inventory"], color="#2196F3", linewidth=2, label="Inventory")
ax1.axhline(40, color="orange", linestyle="--", linewidth=1.2, label="Reorder Point (s=40)")
ax1.axhline(120, color="green", linestyle="--", linewidth=1.2, label="Order-Up-To (S=120)")
ax1.fill_between(df.index, 0, df["Inventory"], alpha=0.15, color="#2196F3")
ax1.set_title("Inventory Level Over Time")
ax1.set_ylabel("Units")
ax1.set_xlabel("Day")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# 2. Backlog
ax2 = fig.add_subplot(gs[1, 0])
ax2.fill_between(df.index, df["Backlog"], color="#F44336", alpha=0.6, label="Backlog")
ax2.plot(df.index, df["Backlog"], color="#F44336", linewidth=1.5)
ax2.set_title("Backlog (Unmet Demand)")
ax2.set_ylabel("Units")
ax2.set_xlabel("Day")
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

# 3. Daily demand
ax3 = fig.add_subplot(gs[1, 1])
ax3.bar(df.index, df["TotalDemand"], color="#9C27B0", alpha=0.7, label="Daily Demand")
ax3.set_title("Total Daily Demand (5 Customers)")
ax3.set_ylabel("Units")
ax3.set_xlabel("Day")
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# 4. Cumulative costs
ax4 = fig.add_subplot(gs[2, 0])
ax4.plot(df.index, df["HoldingCost"], color="#4CAF50", linewidth=2, label="Holding Cost")
ax4.plot(df.index, df["BacklogCost"], color="#FF5722", linewidth=2, label="Backlog Cost")
ax4.plot(df.index, df["HoldingCost"] + df["BacklogCost"],
         color="#333333", linewidth=2, linestyle="--", label="Total Cost")
ax4.set_title("Cumulative Costs")
ax4.set_ylabel("$ Cost")
ax4.set_xlabel("Day")
ax4.legend(fontsize=9)
ax4.grid(True, alpha=0.3)

# 5. Order events
ax5 = fig.add_subplot(gs[2, 1])
order_days = df[df["OrderPlaced"] == 1].index
ax5.vlines(order_days, 0, 1, color="#FF9800", linewidth=2, label=f"Order Placed ({len(order_days)} times)")
ax5.set_title("Reorder Events")
ax5.set_xlabel("Day")
ax5.set_yticks([])
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/simulation_results.png", dpi=150, bbox_inches="tight")
plt.show()
print("\n📊 Chart saved → outputs/simulation_results.png")


# ── CELL 6: Scenario comparison (normal vs disruption)
print("\n" + "=" * 55)
print("  SCENARIO COMPARISON: Normal vs Disruption")
print("=" * 55)

scenarios = {
    "Baseline (LT=3)":    SupplyChainModel(lead_time=3,  seed=42),
    "Disruption (LT=7)":  SupplyChainModel(lead_time=7,  seed=42),
    "Low Capacity":       SupplyChainModel(lead_time=3, supplier_cap=60, seed=42),
}

fig2, axes = plt.subplots(1, 3, figsize=(15, 4))
fig2.suptitle("Scenario Comparison — Inventory Level", fontsize=13, fontweight="bold")

colors = ["#2196F3", "#F44336", "#FF9800"]
for ax, (name, m), color in zip(axes, scenarios.items(), colors):
    result = m.run(steps=90)
    ax.plot(result.index, result["Inventory"], color=color, linewidth=2)
    ax.axhline(40, color="gray", linestyle="--", linewidth=1, alpha=0.7)
    ax.fill_between(result.index, 0, result["Inventory"], alpha=0.15, color=color)
    service = 100 * (1 - (result["Backlog"] > 0).mean())
    ax.set_title(f"{name}\nService Level: {service:.1f}%")
    ax.set_ylabel("Inventory")
    ax.set_xlabel("Day")
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/scenario_comparison.png", dpi=150, bbox_inches="tight")
plt.show()
print("📊 Scenario chart saved → outputs/scenario_comparison.png")
print("\n✅ All done!")
