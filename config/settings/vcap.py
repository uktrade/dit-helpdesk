import json

from .env import env


VCAP_SERVICES = json.loads(env.str("VCAP_SERVICES"))

ES_URL = VCAP_SERVICES["elasticsearch"][0]["credentials"]["uri"]
REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]

s3_data = VCAP_SERVICES["aws-s3-bucket"][0]["credentials"]
AWS_ALT_TARIFF_BUCKET_NAME = s3_data["bucket_name"]
AWS_REGION = s3_data["aws_region"]
AWS_ACCESS_KEY_ID = s3_data["aws_access_key_id"]
AWS_SECRET_ACCESS_KEY = s3_data["aws_secret_access_key"]
