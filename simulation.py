"""
Supply Chain Inventory Simulation using Mesa (Agent-Based Modeling)
-------------------------------------------------------------------
Agents:
  - SupplierAgent  : fills orders, has limited production capacity
  - RetailerAgent  : places orders based on inventory level (reorder point policy)
  - CustomerAgent  : generates random daily demand
"""

import random
import pandas as pd
from mesa import Agent, Model
from mesa.datacollection import DataCollector


# ─────────────────────────────────────────────
# AGENTS
# ─────────────────────────────────────────────

class CustomerAgent(Agent):
    """Generates stochastic daily demand."""

    def __init__(self, model, mean_demand=20, std_demand=5):
        super().__init__(model)
        self.mean_demand = mean_demand
        self.std_demand = std_demand
        self.daily_demand = 0

    def step(self):
        self.daily_demand = max(0, int(random.gauss(self.mean_demand, self.std_demand)))


class SupplierAgent(Agent):
    """Receives orders from retailers and fulfils them up to capacity."""

    def __init__(self, model, capacity=150):
        super().__init__(model)
        self.capacity = capacity
        self.pending_orders = []   # list of (retailer, qty, due_day)
        self.total_shipped = 0

    def receive_order(self, retailer, qty, lead_time):
        due_day = self.model.steps + lead_time
        self.pending_orders.append((retailer, qty, due_day))

    def step(self):
        current_day = self.model.steps
        remaining_capacity = self.capacity
        still_pending = []

        for (retailer, qty, due_day) in self.pending_orders:
            if due_day <= current_day and remaining_capacity > 0:
                shipped = min(qty, remaining_capacity)
                retailer.receive_shipment(shipped)
                remaining_capacity -= shipped
                self.total_shipped += shipped
                if shipped < qty:
                    still_pending.append((retailer, qty - shipped, due_day + 1))
            else:
                still_pending.append((retailer, qty, due_day))

        self.pending_orders = still_pending


class RetailerAgent(Agent):
    """
    Manages inventory using a classic (s, S) reorder-point policy.

    s = reorder point  → order when inventory drops below s
    S = order-up-to    → order enough to reach S
    """

    def __init__(self, model, supplier,
                 initial_inventory=100,
                 reorder_point=40,
                 order_up_to=120,
                 lead_time=3,
                 holding_cost=1.0,
                 backlog_cost=5.0):
        super().__init__(model)
        self.supplier = supplier
        self.inventory = initial_inventory
        self.reorder_point = reorder_point
        self.order_up_to = order_up_to
        self.lead_time = lead_time
        self.holding_cost = holding_cost
        self.backlog_cost = backlog_cost

        self.backlog = 0
        self.total_holding_cost = 0.0
        self.total_backlog_cost = 0.0
        self.total_sales = 0
        self.order_placed_today = False

    def receive_shipment(self, qty):
        self.inventory += qty
        fulfilled = min(self.backlog, qty)
        self.backlog -= fulfilled

    def step(self):
        # 1. Aggregate customer demand
        total_demand = sum(
            c.daily_demand for c in self.model.agents
            if isinstance(c, CustomerAgent)
        )

        # 2. Fulfil demand
        fulfilled = min(total_demand, self.inventory)
        self.total_sales += fulfilled
        self.inventory -= fulfilled
        self.backlog += total_demand - fulfilled

        # 3. Costs
        self.total_holding_cost += self.inventory * self.holding_cost
        self.total_backlog_cost += self.backlog * self.backlog_cost

        # 4. Reorder decision (s, S policy)
        self.order_placed_today = False
        if self.inventory < self.reorder_point:
            order_qty = self.order_up_to - self.inventory
            self.supplier.receive_order(self, order_qty, self.lead_time)
            self.order_placed_today = True


# ─────────────────────────────────────────────
# MODEL
# ─────────────────────────────────────────────

class SupplyChainModel(Model):
    """
    Ties together one Supplier, one Retailer, and N Customers.

    Parameters
    ----------
    n_customers     : number of customer agents
    mean_demand     : average daily demand per customer
    std_demand      : demand standard deviation
    reorder_point   : inventory level that triggers an order
    order_up_to     : target inventory after reordering
    lead_time       : days between order and delivery
    supplier_cap    : max units the supplier ships per day
    seed            : random seed for reproducibility
    """

    def __init__(self,
                 n_customers=5,
                 mean_demand=20,
                 std_demand=5,
                 reorder_point=40,
                 order_up_to=120,
                 lead_time=3,
                 supplier_cap=150,
                 seed=42):
        super().__init__(rng=seed)
        random.seed(seed)

        # Create supplier
        self.supplier = SupplierAgent(self, capacity=supplier_cap)

        # Create retailer
        self.retailer = RetailerAgent(
            self, self.supplier,
            reorder_point=reorder_point,
            order_up_to=order_up_to,
            lead_time=lead_time
        )

        # Create customers
        for _ in range(n_customers):
            CustomerAgent(self, mean_demand=mean_demand, std_demand=std_demand)

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Inventory":   lambda m: m.retailer.inventory,
                "Backlog":     lambda m: m.retailer.backlog,
                "HoldingCost": lambda m: m.retailer.total_holding_cost,
                "BacklogCost": lambda m: m.retailer.total_backlog_cost,
                "TotalDemand": lambda m: sum(
                    c.daily_demand for c in m.agents
                    if isinstance(c, CustomerAgent)),
                "OrderPlaced": lambda m: int(m.retailer.order_placed_today),
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.agents.do("step")

    def run(self, steps=90):
        for _ in range(steps):
            self.step()
        return self.datacollector.get_model_vars_dataframe()
