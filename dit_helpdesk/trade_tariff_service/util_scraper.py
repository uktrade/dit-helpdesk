import logging

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

COMMODITY_URL = "https://www.trade-tariff.service.gov.uk/" "commodities/%s.json"
