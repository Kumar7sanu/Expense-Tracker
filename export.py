import json
from collections import defaultdict

import db


# ----------------------------
# Load Config
# ----------------------------

with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


# ----------------------------
# Build Analytics
# ----------------------------

def build_stats(data):

    income = 0
    expense = 0

    category_totals = defaultdict(float)
    merchant_totals = defaultdict(float)
    monthly_totals = defaultdict(float)

    for txn in data:

        amount = float(txn["amount"])

        if txn["type"] == "income":
            income += amount
            continue

        expense += amount

        category_totals[txn["category"]] += amount
        merchant_totals[txn["merchant"]] += amount
        monthly_totals[txn["month"]] += amount

    savings = income - expense

    budget = CONFIG["monthlyBudget"]

    budget_left = budget - expense

    daily_average = round(expense / 14, 2) if expense else 0

    projected = round(daily_average * 30, 2)

    top_category = None
    top_merchant = None

    if category_totals:
        top_category = max(
            category_totals,
            key=category_totals.get
        )

    if merchant_totals:
        top_merchant = max(
            merchant_totals,
            key=merchant_totals.get
        )

    return {

        "income": income,

        "expense": expense,

        "savings": savings,

        "budget": budget,

        "budgetLeft": budget_left,

        "dailyAverage": daily_average,

        "projected": projected,

        "topCategory": top_category,

        "topMerchant": top_merchant,

        "categoryTotals": dict(category_totals),

        "merchantTotals": dict(merchant_totals),

        "monthlyTotals": dict(monthly_totals)

    }


# ----------------------------
# Export
# ----------------------------

def export():

    data = db.get_all()

    stats = build_stats(data)

    output = []

    output.append(
        "window.EXPENSE_DATA="
        + json.dumps(data, indent=2)
        + ";"
    )

    output.append("")

    output.append(
        "window.EXPENSE_STATS="
        + json.dumps(stats, indent=2)
        + ";"
    )

    output.append("")

    output.append(
        "window.EXPENSE_CONFIG="
        + json.dumps(
            {
                "currency": CONFIG["currency"],
                "monthlyBudget": CONFIG["monthlyBudget"],
                "budgets": CONFIG["budgets"],
                "dashboardTitle": CONFIG["dashboardTitle"]
            },
            indent=2
        )
        + ";"
    )

    with open("data.js", "w", encoding="utf-8") as f:

        f.write("\n".join(output))

    print("✓ data.js generated")


# ----------------------------
# Run
# ----------------------------

if __name__ == "__main__":

    export()