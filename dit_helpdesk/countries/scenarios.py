def update_scenario(country):
    if (
        country.scenario == "TRADE_AGREEMENT_NO_ROO_TWUK"
        and country.rules_documents.exists()
    ):
        country.scenario = "TRADE_AGREEMENT"
        country.save()
