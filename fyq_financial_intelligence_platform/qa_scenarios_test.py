from services.financial_service import build_income, build_balance, build_cashflow
from core.decision_intelligence import executive_summary

scenarios = {

"PROFITABLE": {
"income": {
"revenue":1000000,
"cogs":400000,
"opex":200000,
"depreciation":50000,
"interest":30000,
"tax_rate":15
},
"balance":{
"cash":300000,
"accounts_receivable":200000,
"inventory":100000,
"accounts_payable":100000,
"short_term_debt":50000,
"long_term_debt":150000,
"paid_in_capital":500000,
"retained_earnings":300000,
"fixed_assets":500000
},
"cashflow":{
"net_income":272000,
"depreciation_add_back":50000,
"capex":-100000,
"beginning_cash":200000
}
},


"LOSS_CASE":{
"income":{
"revenue":500000,
"cogs":350000,
"opex":250000,
"depreciation":30000,
"interest":40000,
"tax_rate":15
},
"balance":{
"cash":30000,
"accounts_receivable":50000,
"inventory":80000,
"accounts_payable":150000,
"short_term_debt":200000,
"long_term_debt":300000,
"paid_in_capital":200000,
"retained_earnings":-100000,
"fixed_assets":300000
},
"cashflow":{
"net_income":-170000,
"depreciation_add_back":30000,
"capex":-10000,
"beginning_cash":50000
}

}

}


for name,data in scenarios.items():

    print("\n====================")
    print(name)
    print("====================")

    result = executive_summary(
        data["income"],
        data["balance"],
        data["cashflow"]
    )

    print("STATUS:",result["analysis_status"])
    print("CLASS:",result["classification"])
    print("HEALTH:",result["health_score"])
    print("NARRATIVE:")
    print(result["narrative"])

    print("\nRISKS:")
    for r in result["risks"]:
        print("-",r)

    print("\nPRIORITIES:")
    for p in result["priorities"]:
        print("-",p)
