import json
from core.decision_intelligence import executive_summary, scenario_analysis


with open("manufacturing_result_clean.json") as f:
    base=json.load(f)


scenarios = [

    {
        "name":"BASE CASE - الوضع الأساسي",
        "changes":{}
    },

    {
        "name":"GROWTH +20% REVENUE",
        "changes":{
            "revenue_pct":20
        }
    },

    {
        "name":"COST PRESSURE +15% COGS",
        "changes":{
            "cogs_pct":15
        }
    },

    {
        "name":"EFFICIENCY -10% OPEX",
        "changes":{
            "opex_pct":-10
        }
    },

    {
        "name":"STRESS CASE",
        "changes":{
            "revenue_pct":-20,
            "cogs_pct":15,
            "opex_pct":10,
            "financing_pct":30
        }
    }
]


print("="*70)
print("FYQ v9.8 FINAL SCENARIO QA")
print("="*70)


for s in scenarios:

    print("\n")
    print("="*40)
    print(s["name"])
    print("="*40)

    try:

        result=scenario_analysis(
            base["income"],
            base["balance"],
            base["cashflow"],
            s["changes"]
        )

        metrics=result["scenario"]

        print("Revenue:",
              metrics.get("revenue"))

        print("EBITDA:",
              metrics.get("ebitda"))

        print("Net Income:",
              metrics.get("net_income"))

        print("FCF:",
              metrics.get("free_cash_flow"))

        print("Debt/Equity:",
              metrics.get("debt_to_equity"))

        print("STATUS: PASS")


    except Exception as e:

        print("STATUS: FAIL")
        print("ERROR:",e)


print("\n")
print("="*70)
print("QA COMPLETE")
print("="*70)

