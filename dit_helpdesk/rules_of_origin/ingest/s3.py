import boto3


def _get_s3_bucket(bucket_name, access_key_id, access_key, **resource_kwargs):

    # If the given endpoint url is empty, remove it from the arg list to use the default s3 endpoint
    if resource_kwargs["endpoint_url"] == "":
        resource_kwargs.pop("endpoint_url")

    s3_session = boto3.Session(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key,
    )

    s3_resource = s3_session.resource("s3", **resource_kwargs)
    s3_bucket = s3_resource.Bucket(bucket_name)

    return s3_bucket
