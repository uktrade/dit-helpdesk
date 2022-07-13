import boto3
import logging

logger = logging.getLogger(__name__)


def _get_s3_bucket(bucket_name, access_key_id, access_key, **resource_kwargs):

    logger.critical("*****************************************************")
    logger.critical("*****************************************************")
    logger.critical("*****************************************************")
    logger.critical("*****************************************************")
    logger.critical("*****************************************************")
    logger.critical("THE URL: " + str(resource_kwargs["endpoint_url"]))
    logger.critical("THE NAME: " + str(bucket_name))

    # If the given endpoint url is empty, remove it from the arg list to use the default s3 endpoint
    if resource_kwargs["endpoint_url"] == "":
        resource_kwargs.pop("endpoint_url")

    s3_session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key,
    )

    logger.critical("THE SESSION:" + str(s3_session))

    s3_resource = s3_session.resource("s3", **resource_kwargs)
    s3_bucket = s3_resource.Bucket(bucket_name)

    logger.critical("THE RESOURCE: " + str(s3_resource))
    logger.critical("THE BUCKET: " + str(s3_bucket))
    logger.critical("-")
    for thing in s3_bucket.objects.all():
        logger.critical(str(thing))

    # IT CAN ACCESS THE BUCKET, BUT FOR SOME REASON THINKS THE BUCKET IS EMPTY
    # LITERALLY NOTHING HAS CHANGED - THIS WILL FAIL ON MASTER IF RE-RAN
    # SEE PR FOR "INDICATE FAILING TESTS" FOR THAT CAR CRASH.
    # WE KNOW THE BUCKET EXISTS AS IT DOESN'T ERROR. THE LOG OUTPUT ON LOCAL
    # DOCKER LOOKS LIKE THIS:
    #
    # THE URL: http://host.docker.internal:9000
    # THE NAME: test-bucket-roo-import-missing-prefix
    # THE SESSION:Session(region_name=None)
    # THE RESOURCE: s3.ServiceResource()
    # THE BUCKETs3.Bucket(name='test-bucket-roo-import-missing-prefix')
    # -
    # s3.ObjectSummary(bucket_name='test-bucket-roo-import-missing-prefix',
    #                   key='rules_of_origin_incorrect_prefix/.gitkeep')
    #
    #
    #
    #
    #
    # THE LOG OUTPUT ON CIRCLE IS:
    #
    # THE URL: http://s3:9000
    # THE NAME: test-bucket-roo-import-missing-prefix
    # THE SESSION:Session(region_name=None)
    # THE RESOURCE: s3.ServiceResource()
    # THE BUCKET: s3.Bucket(name='test-bucket-roo-import-missing-prefix')
    # -

    logger.critical("*****************************************************")
    logger.critical("*****************************************************")
    logger.critical("*****************************************************")
    logger.critical("*****************************************************")
    logger.critical("*****************************************************")

    return s3_bucket
