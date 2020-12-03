import json

from .env import env


VCAP_SERVICES = json.loads(env.str("VCAP_SERVICES"))
ES_URL = VCAP_SERVICES["elasticsearch"][0]["credentials"]["uri"]
REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]
