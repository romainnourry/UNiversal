import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import numpy as np
import random

# ---------------------------
# Agent Definitions
# ---------------------------
class PersonAgent(Agent):
    def __init__(self, unique_id, model, income, rent):
        super().__init__(unique_id, model)
        self.income = income
        self.rent = rent
        self.capital_investment = income * random.uniform(0.0, 0.1)
        self.universals = 0
        self.spending_rate = random.uniform(0.5, 0.85)
        self.universal_spending_propensity = random.uniform(0.4, 0.9)

    def step(self):
        target_ci = self.income * 0.25
        gap = max(0, target_ci - self.capital_investment)
        self.universals += gap * 0.5
        self.spending = self.income * self.spending_rate
        self.universal_spending = self.spending * self.universal_spending_propensity * 0.2
        self.universals = max(0, self.universals - self.universal_spending)

class BusinessAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.annual_revenue = random.randint(100000, 300000)
        self.capitalization = self.annual_revenue * random.uniform(0.05, 0.15)
        self.accepts_universals = True
        self.universals_received = 0

    def step(self):
        universal_income = random.randint(100, 1000)
        self.universals_received += universal_income

class LandlordAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.monthly_rent_collected = 0
        self.reinvestment_rate = random.uniform(0.05, 0.3)

    def step(self):
        self.monthly_rent_collected = random.randint(10000, 30000)
        self.local_reinvestment = self.monthly_rent_collected * self.reinvestment_rate

# ---------------------------
# Model Definition
# ---------------------------
class HarlemModel(Model):
    def __init__(self, num_people, num_businesses, num_landlords):
        self.schedule = RandomActivation(self)

        for i in range(num_people):
            income = random.randint(20000, 50000)
            rent = random.randint(800, 2000)
            agent = PersonAgent(i, self, income, rent)
            self.schedule.add(agent)

        for i in range(num_businesses):
            business = BusinessAgent(i + num_people, self)
            self.schedule.add(business)

        for i in range(num_landlords):
            landlord = LandlordAgent(i + num_people + num_businesses, self)
            self.schedule.add(landlord)

        self.datacollector = DataCollector(
            model_reporters={
                "Total_Universals": self.total_universals,
                "Gini_Income": self.gini_income,
                "Gini_Wealth": self.gini_wealth,
                "Total_Rent": self.total_rent_collected,
                "Avg_Business_Growth": self.avg_business_growth
            },
            agent_reporters={
                "Income": lambda a: getattr(a, 'income', None),
                "Capital": lambda a: getattr(a, 'capital_investment', None),
                "Universals": lambda a: getattr(a, 'universals', None),
                "Spending": lambda a: getattr(a, 'spending', None),
                "Universal_Spending": lambda a: getattr(a, 'universal_spending', None),
                "Rent": lambda a: getattr(a, 'rent', None)
            }
        )

    def total_universals(self):
        return sum([getattr(a, 'universals', 0) for a in self.schedule.agents if hasattr(a, 'universals')])

    def total_rent_collected(self):
        return sum([getattr(a, 'rent', 0) for a in self.schedule.agents if hasattr(a, 'rent')])

    def gini_income(self):
        incomes = [a.income for a in self.schedule.agents if hasattr(a, 'income')]
        return self.gini(incomes)

    def gini_wealth(self):
        wealths = [getattr(a, 'capital_investment', 0) + getattr(a, 'universals', 0) for a in self.schedule.agents if hasattr(a, 'capital_investment')]
        return self.gini(wealths)

    def avg_business_growth(self):
        growth = [a.universals_received for a in self.schedule.agents if hasattr(a, 'universals_received')]
        return np.mean(growth) if growth else 0

    def gini(self, x):
        if len(x) == 0:
            return 0
        x = sorted(x)
        n = len(x)
        cumulative = np.cumsum(x)
        gini_index = (2 * sum((i + 1) * x[i] for i in range(n)) / (n * sum(x))) - (n + 1) / n
        return gini_index

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# ---------------------------
# Streamlit Interface
# ---------------------------
st.set_page_config(page_title="Harlem Economic Simulation", layout="wide")
st.title("Universal Capital Simulation – Harlem Model")

num_people = st.sidebar.slider("Number of residents", 100, 1000, 500)
num_businesses = st.sidebar.slider("Number of businesses", 10, 200, 100)
num_landlords = st.sidebar.slider("Number of landlords", 1, 20, 10)
num_steps = st.sidebar.slider("Simulation steps (e.g., months)", 1, 50, 12)

model = HarlemModel(num_people, num_businesses, num_landlords)
for _ in range(num_steps):
    model.step()

agent_df = model.datacollector.get_agent_vars_dataframe().reset_index()
model_df = model.datacollector.get_model_vars_dataframe().reset_index()

st.subheader("Total Universals Issued Over Time")
st.line_chart(model_df.set_index("Step")["Total_Universals"])

st.subheader("Gini Coefficients")
st.write("**Income Inequality** (0 = perfect equality, 1 = perfect inequality):", round(model_df["Gini_Income"].iloc[-1], 3))
st.write("**Wealth Inequality (including universals)**:", round(model_df["Gini_Wealth"].iloc[-1], 3))

st.subheader("Final Agent Data Snapshot")
final_agents = agent_df.groupby("AgentID").last().sort_values("Universals", ascending=False)
st.dataframe(final_agents)

st.subheader("Universal Spending Potential Distribution")
st.bar_chart(final_agents["Universal_Spending"].fillna(0))

st.subheader("Business Growth from Universals")
st.write("Average universals received by businesses:", round(model_df["Avg_Business_Growth"].iloc[-1], 2))

st.caption("This simulation models a Harlem-like neighborhood with residents, businesses, and landlords, quantifying inequality, capital access, and the systemic effect of universal capital redistribution.")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import numpy as np
import random

# ---------------------------
# Agent Definitions
# ---------------------------
class PersonAgent(Agent):
    def __init__(self, unique_id, model, income, rent):
        super().__init__(unique_id, model)
        self.income = income
        self.rent = rent
        self.capital_investment = income * random.uniform(0.0, 0.1)
        self.universals = 0
        self.spending_rate = random.uniform(0.5, 0.85)
        self.universal_spending_propensity = random.uniform(0.4, 0.9)

    def step(self):
        target_ci = self.income * 0.25
        gap = max(0, target_ci - self.capital_investment)
        self.universals += gap * 0.5
        self.spending = self.income * self.spending_rate
        self.universal_spending = self.spending * self.universal_spending_propensity * 0.2
        self.universals = max(0, self.universals - self.universal_spending)

class BusinessAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.annual_revenue = random.randint(100000, 300000)
        self.capitalization = self.annual_revenue * random.uniform(0.05, 0.15)
        self.accepts_universals = True
        self.universals_received = 0

    def step(self):
        universal_income = random.randint(100, 1000)
        self.universals_received += universal_income

class LandlordAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.monthly_rent_collected = 0
        self.reinvestment_rate = random.uniform(0.05, 0.3)

    def step(self):
        self.monthly_rent_collected = random.randint(10000, 30000)
        self.local_reinvestment = self.monthly_rent_collected * self.reinvestment_rate

# ---------------------------
# Model Definition
# ---------------------------
class HarlemModel(Model):
    def __init__(self, num_people, num_businesses, num_landlords):
        self.schedule = RandomActivation(self)

        for i in range(num_people):
            income = random.randint(20000, 50000)
            rent = random.randint(800, 2000)
            agent = PersonAgent(i, self, income, rent)
            self.schedule.add(agent)

        for i in range(num_businesses):
            business = BusinessAgent(i + num_people, self)
            self.schedule.add(business)

        for i in range(num_landlords):
            landlord = LandlordAgent(i + num_people + num_businesses, self)
            self.schedule.add(landlord)

        self.datacollector = DataCollector(
            model_reporters={
                "Total_Universals": self.total_universals,
                "Gini_Income": self.gini_income,
                "Gini_Wealth": self.gini_wealth,
                "Total_Rent": self.total_rent_collected,
                "Avg_Business_Growth": self.avg_business_growth
            },
            agent_reporters={
                "Income": lambda a: getattr(a, 'income', None),
                "Capital": lambda a: getattr(a, 'capital_investment', None),
                "Universals": lambda a: getattr(a, 'universals', None),
                "Spending": lambda a: getattr(a, 'spending', None),
                "Universal_Spending": lambda a: getattr(a, 'universal_spending', None),
                "Rent": lambda a: getattr(a, 'rent', None)
            }
        )

    def total_universals(self):
        return sum([getattr(a, 'universals', 0) for a in self.schedule.agents if hasattr(a, 'universals')])

    def total_rent_collected(self):
        return sum([getattr(a, 'rent', 0) for a in self.schedule.agents if hasattr(a, 'rent')])

    def gini_income(self):
        incomes = [a.income for a in self.schedule.agents if hasattr(a, 'income')]
        return self.gini(incomes)

    def gini_wealth(self):
        wealths = [getattr(a, 'capital_investment', 0) + getattr(a, 'universals', 0) for a in self.schedule.agents if hasattr(a, 'capital_investment')]
        return self.gini(wealths)

    def avg_business_growth(self):
        growth = [a.universals_received for a in self.schedule.agents if hasattr(a, 'universals_received')]
        return np.mean(growth) if growth else 0

    def gini(self, x):
        if len(x) == 0:
            return 0
        x = sorted(x)
        n = len(x)
        cumulative = np.cumsum(x)
        gini_index = (2 * sum((i + 1) * x[i] for i in range(n)) / (n * sum(x))) - (n + 1) / n
        return gini_index

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# ---------------------------
# Streamlit Interface
# ---------------------------
st.set_page_config(page_title="Harlem Economic Simulation", layout="wide")
st.title("Universal Capital Simulation – Harlem Model")

num_people = st.sidebar.slider("Number of residents", 100, 1000, 500)
num_businesses = st.sidebar.slider("Number of businesses", 10, 200, 100)
num_landlords = st.sidebar.slider("Number of landlords", 1, 20, 10)
num_steps = st.sidebar.slider("Simulation steps (e.g., months)", 1, 50, 12)

model = HarlemModel(num_people, num_businesses, num_landlords)
for _ in range(num_steps):
    model.step()

agent_df = model.datacollector.get_agent_vars_dataframe().reset_index()
model_df = model.datacollector.get_model_vars_dataframe().reset_index()

st.subheader("Total Universals Issued Over Time")
st.line_chart(model_df.set_index("Step")["Total_Universals"])

st.subheader("Gini Coefficients")
st.write("**Income Inequality** (0 = perfect equality, 1 = perfect inequality):", round(model_df["Gini_Income"].iloc[-1], 3))
st.write("**Wealth Inequality (including universals)**:", round(model_df["Gini_Wealth"].iloc[-1], 3))

st.subheader("Final Agent Data Snapshot")
final_agents = agent_df.groupby("AgentID").last().sort_values("Universals", ascending=False)
st.dataframe(final_agents)

st.subheader("Universal Spending Potential Distribution")
st.bar_chart(final_agents["Universal_Spending"].fillna(0))

st.subheader("Business Growth from Universals")
st.write("Average universals received by businesses:", round(model_df["Avg_Business_Growth"].iloc[-1], 2))

st.caption("This simulation models a Harlem-like neighborhood with residents, businesses, and landlords, quantifying inequality, capital access, and the systemic effect of universal capital redistribution.")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

# Define Person agent
class PersonAgent(Agent):
    def __init__(self, unique_id, model, income, capital_investment):
        super().__init__(unique_id, model)
        self.income = income
        self.capital_investment = capital_investment
        self.universals = 0

    def step(self):
        target_ci = self.income * 0.25
        gap = max(0, target_ci - self.capital_investment)
        self.universals += gap * 0.5

# Define Town model
class TownModel(Model):
    def __init__(self, N):
        self.num_agents = N
        self.schedule = RandomActivation(self)

        for i in range(self.num_agents):
            income = self.random.randint(1500, 6000)
            capital = income * self.random.uniform(0.0, 0.4)
            agent = PersonAgent(i, self, income, capital)
            self.schedule.add(agent)

        self.datacollector = DataCollector(
            model_reporters={"Total_Universals": self.total_universals},
            agent_reporters={"Income": "income", "Capital": "capital_investment", "Universals": "universals"}
        )

    def total_universals(self):
        return sum(agent.universals for agent in self.schedule.agents)

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# Streamlit UI
st.title("Universal Capital Simulation")
num_agents = st.slider("Number of agents", 10, 500, 100)
num_steps = st.slider("Simulation steps", 1, 50, 10)

model = TownModel(num_agents)
for _ in range(num_steps):
    model.step()

agent_df = model.datacollector.get_agent_vars_dataframe()
model_df = model.datacollector.get_model_vars_dataframe()

st.subheader("Total Universals Over Time")
st.line_chart(model_df)

st.subheader("Final Agent Snapshot")
latest = agent_df.reset_index().groupby("AgentID").last()
st.dataframe(latest.sort_values("Universals", ascending=False))
