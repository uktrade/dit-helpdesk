import json

from .env import env


VCAP_SERVICES = json.loads(env.str("VCAP_SERVICES"))

ES_URL = VCAP_SERVICES["opensearch"][0]["credentials"]["uri"]
REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]

try:
    roo_s3_config = VCAP_SERVICES["aws-s3-bucket"][0]
except KeyError:
    ROO_S3_BUCKET_NAME = ""
    ROO_S3_ACCESS_KEY_ID = ""
    ROO_S3_SECRET_ACCESS_KEY = ""
else:
    roo_s3_credentials = roo_s3_config["credentials"]
    ROO_S3_BUCKET_NAME = roo_s3_credentials["bucket_name"]
    ROO_S3_ACCESS_KEY_ID = roo_s3_credentials["aws_access_key_id"]
    ROO_S3_SECRET_ACCESS_KEY = roo_s3_credentials["aws_secret_access_key"]
