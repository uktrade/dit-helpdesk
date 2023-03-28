import json

from .env import env

VCAP_SERVICES = json.loads(env.str("VCAP_SERVICES"))

ES_URL = VCAP_SERVICES["opensearch"][0]["credentials"]["uri"]


# Copilot env key.  IF set, we turn the supplied json into a DB connection string
# that can be consumed by dj-database-url
DATABASE_CREDS = env.json("DATABASE_CREDENTIALS", default={})

if DATABASE_CREDS:
    db_url = "{engine}://{username}:{password}@{host}:{port}/{dbname}".format(**DATABASE_CREDS)
    os.environ["DATABASE_URL"] = db_url
    
# Redis
if "redis" in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]
else:
    REDIS_URL = env("REDIS_ENDPOINT", default=None)

# COPILOT configuration
# if not CELERY_BROKER_URL:
#     CELERY_BROKER_URL = env("REDIS_ENDPOINT")

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": CELERY_BROKER_URL,
#         "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
#         "KEY_PREFIX": "wp_",
#     }
# }

DATABASES = {"default": env.db()}

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
