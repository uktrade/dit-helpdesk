class ScenarioTransitioner:
    def __init__(self):
        self.transitions = {}

    def __call__(self, from_scenario, to_scenario):
        def register_condition(func):
            self.transitions[from_scenario] = (
                func,
                to_scenario,
            )

            return func

        return register_condition

    def run(self, country):
        try:
            condition, to_scenario = self.transitions[country.scenario]
        except KeyError:
            return

        if condition(country):
            country.scenario = to_scenario
            country.save()


transition_scenario = ScenarioTransitioner()


@transition_scenario("TRADE_AGREEMENT_NO_ROO_TWUK", "TRADE_AGREEMENT")
def has_rules_of_origin(country):
    return country.rules_documents.exists()


def update_scenario(country):
    transition_scenario.run(country)
