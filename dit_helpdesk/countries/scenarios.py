import requests


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
def _has_rules_of_origin(country):
    return country.rules_documents.exists()


def _get_geographical_area_country_codes(area_id):
    geographical_areas_response = requests.get(
        "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas"
    )
    geographical_areas = geographical_areas_response.json()["data"]

    area_data = [area for area in geographical_areas if area["id"] == area_id][0]
    country_codes = [
        child_area["id"]
        for child_area in area_data["relationships"]["children_geographical_areas"][
            "data"
        ]
    ]

    return country_codes


@transition_scenario("DOM_LEG_GSP_WITH_EXCLUSIONS", "GSP")
def _is_in_enhanced_framework(country):
    enhanced_framework_id = "2027"
    enhanced_framework_country_codes = _get_geographical_area_country_codes(
        enhanced_framework_id
    )

    return country.country_code in enhanced_framework_country_codes


@transition_scenario("TRADE_AGREEMENT_GSP_TRANS", "TRADE_AGREEMENT")
def _is_not_in_gsp(country):
    enhanced_framework_id = "2020"
    enhanced_framework_country_codes = _get_geographical_area_country_codes(
        enhanced_framework_id
    )

    return country.country_code not in enhanced_framework_country_codes


def update_scenario(country):
    transition_scenario.run(country)
