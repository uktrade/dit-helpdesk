import logging
import requests

from string import ascii_lowercase

from django.conf import settings

logger = logging.getLogger(__name__)


class MissingSynonymsException(Exception):
    def __init__(self, message):
        super().__init__(message)


class SynonymBuilder:
    def __init__(self):
        pass

    def get_synonyms_list(self):
        # Function to call that will create and return the synonyms csv
        logger.info("Building the synonyms CSV through the Trade Tariff API")

        # Get the correct URL for the Trade Tariff Service
        trade_tariff_urls = settings.TRADE_TARIFF_CONFIG()
        trade_tariff_url = trade_tariff_urls["UK"]["TREE"]["BASE_URL"]

        # Set up counters for logging purposes
        heading_synonym_count = chapter_synonym_count = commodity_synonym_count = 0

        synonyms_list = []

        # Loop through every letter in the alphabet to call the TTS-API which will only
        # accept single letter arguments in a request
        for letter in ascii_lowercase:
            search_references_url = (
                f"{trade_tariff_url}search_references.json?query[letter]={letter}"
            )
            search_references_response = requests.get(search_references_url)
            search_reference_details = search_references_response.json()["data"]

            # Need to loop through the commodity details data and extract the 4 digit referenced_id and title
            # but CURRENTLY only for Headings (commodity and chapters can come later)
            for search_reference in search_reference_details:
                if search_reference["attributes"]["referenced_class"] == "Heading":
                    synonym = search_reference["attributes"]["title"]
                    four_digit_code = search_reference["attributes"]["referenced_id"]

                    # Add decimal in middle of 4 digit code
                    four_digit_code = four_digit_code[:2] + "." + four_digit_code[2:]
                    row = [four_digit_code, synonym]
                    synonyms_list.append(row)
                    heading_synonym_count += 1

                elif search_reference["attributes"]["referenced_class"] == "Chapter":
                    chapter_synonym_count += 1

                elif search_reference["attributes"]["referenced_class"] == "Commodity":
                    commodity_synonym_count += 1

        logger.info(
            f"""Completed building the synonyms CSV. There are {heading_synonym_count}
            synonyms to be converted to search keywords. There were {chapter_synonym_count} synonyms
            ignored as they had Chapter level reference codes (2 digits). There were {commodity_synonym_count}
            synonyms ignored as they had Commodity level reference codes (more than 4 digits)."""
        )

        if heading_synonym_count == 0:
            # If we have no usable synonyms, there is a problem and we need to error
            # If carried on, there will be no error, we will just have an empty set of keywords
            raise MissingSynonymsException(
                "There were no usable synonyms returned by the Trade Tariff API, cancelling keyword generation."
            )

        logger.info("Returning synonyms list.")
        return synonyms_list
