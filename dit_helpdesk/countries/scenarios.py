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


GSP_GENERAL_ID = "2020"
GSP_LDC_ID = "2005"
GSP_ENHANCED_ID = "2027"

ALL_GSP_IDS = [GSP_GENERAL_ID, GSP_LDC_ID, GSP_ENHANCED_ID]


def _get_geographical_area_country_codes(area_id):
    geographical_areas_response = requests.get(
        "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas"
    )
    geographical_areas = geographical_areas_response.json()["data"]

    try:
        area_data = [area for area in geographical_areas if area["id"] == area_id][0]
    except IndexError:
        return []

    country_codes = [
        child_area["id"]
        for child_area in area_data["relationships"]["children_geographical_areas"][
            "data"
        ]
    ]

    return country_codes


@transition_scenario("DOM_LEG_GSP_WITH_EXCLUSIONS", "GSP")
def _is_in_gsp_enhanced_framework(country):
    enhanced_framework_country_codes = _get_geographical_area_country_codes(
        GSP_ENHANCED_ID
    )

    return country.country_code in enhanced_framework_country_codes


@transition_scenario("TRADE_AGREEMENT_GSP_TRANS", "TRADE_AGREEMENT")
def _is_not_in_gsp_general_framework(country):
    general_framework_country_codes = _get_geographical_area_country_codes(
        GSP_GENERAL_ID
    )

    return country.country_code not in general_framework_country_codes


@transition_scenario("GSP", "NON_PREF")
def _is_not_in_any_gsp(country):
    gsp_ids = ALL_GSP_IDS
    gsp_country_codes = []

    for gsp_id in gsp_ids:
        gsp_country_codes += _get_geographical_area_country_codes(gsp_id)

    return country.country_code not in gsp_country_codes


def update_scenario(country):
    transition_scenario.run(country)
