"""
.. module: bucket_snake.config
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import os
import logging
from functools import wraps

from bucket_snake.util.exceptions import MissingRequiredConfigurationItemException

logging.basicConfig()
log = logging.getLogger("bucket_snake")
log.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


class Config:
    """
    Class for maintaining the configuration for the entire runtime.
    By default, this will set most of the values from the environment variables -- but is also
    configurable via other means.
    Simply import this and use it:
    ```
    from bucket_snake.config import CONFIG
    ```
    """
    def __init__(self):
        # Bucket Snake specific configuration:
        self._blacklisted_source_accounts = os.environ["BLACKLISTED_SOURCE_ACCOUNTS"].split(",") \
            if os.environ.get("BLACKLISTED_SOURCE_ACCOUNTS") else []
        self._blacklisted_bucket_accounts = os.environ["BLACKLISTED_BUCKET_ACCOUNTS"].split(",") \
            if os.environ.get("BLACKLISTED_BUCKET_ACCOUNTS") else []
        self._bucket_snake_policy_name = os.environ.get("BUCKET_SNAKE_POLICY_NAME", "BucketSnake")
        self._sts_policy_name = os.environ.get("STS_POLICY_NAME", "BucketSnakeAssumeRole")
        self._dest_role_description = os.environ.get("DEST_ROLE_DESCRIPTION", "Bucket Snake provisioned role")
        self._bucket_snake_role = os.environ.get("BUCKET_SNAKE_ROLE", "BucketSnake")
        self._bucket_snake_session_name = os.environ.get("BUCKET_SNAKE_SESSION_NAME", "BucketSnake")
        self._iam_region = os.environ.get("IAM_REGION", "us-east-1")

        # Buckets that contain the historical report -- Just give the application access to all of them
        # (At some point in the future we could probably pair down to region, but assume the app could be deployed
        #  to multiple regions and that the app would pick the bucket within the same region)
        # self._app_reports_buckets = os.environ["APP_REPORTS_BUCKETS"].split(",") \
        #     if os.environ.get("APP_REPORTS_BUCKETS") else None  # REQUIRED FIELD
        self._app_reports_buckets = os.environ["APP_REPORTS_BUCKETS"].split(",") \
            if os.environ.get("APP_REPORTS_BUCKETS") else []

        # SWAG bucket config (REQUIRED FIELDS):
        self._swag_bucket = os.environ.get("SWAG_BUCKET")
        self._swag_region = os.environ.get("SWAG_REGION")
        self._swag_data_file = os.environ.get("SWAG_DATA_FILE")

        # Historical S3 reports dump:
        self._reports_bucket = os.environ.get("REPORTS_BUCKET")  # REQUIRED FIELD
        self._reports_region = os.environ.get("REPORTS_REGION")  # REQUIRED FIELD
        self._reports_prefix = os.environ.get("REPORTS_PREFIX", "historical-s3-report.json")

        # Required Fields:
        self.required_fields = [
            "app_reports_buckets",
            "swag_bucket",
            "swag_region",
            "swag_data_file",
            "reports_bucket",
            "reports_region"
        ]

    @property
    def blacklisted_source_accounts(self):
        return self._blacklisted_source_accounts

    @blacklisted_source_accounts.setter
    def blacklisted_source_accounts(self, accounts):
        self._blacklisted_source_accounts = accounts

    @property
    def blacklisted_bucket_accounts(self):
        return self._blacklisted_bucket_accounts

    @blacklisted_bucket_accounts.setter
    def blacklisted_bucket_accounts(self, accounts):
        self._blacklisted_bucket_accounts = accounts

    @property
    def bucket_snake_policy_name(self):
        return self._bucket_snake_policy_name

    @bucket_snake_policy_name.setter
    def bucket_snake_policy_name(self, policy_name):
        self._bucket_snake_policy_name = policy_name

    @property
    def sts_policy_name(self):
        return self._sts_policy_name

    @sts_policy_name.setter
    def sts_policy_name(self, policy_name):
        self._sts_policy_name = policy_name

    @property
    def dest_role_description(self):
        return self._dest_role_description

    @dest_role_description.setter
    def dest_role_description(self, description):
        self._dest_role_description = description

    @property
    def app_reports_buckets(self):
        return self._app_reports_buckets

    @app_reports_buckets.setter
    def app_reports_buckets(self, buckets):
        self._app_reports_buckets = buckets

    @property
    def iam_region(self):
        return self._iam_region

    @iam_region.setter
    def iam_region(self, region):
        self._iam_region = region

    @property
    def swag_bucket(self):
        return self._swag_bucket

    @swag_bucket.setter
    def swag_bucket(self, swag_bucket):
        self._swag_bucket = swag_bucket

    @property
    def swag_region(self):
        return self._swag_region

    @swag_region.setter
    def swag_region(self, region):
        self._swag_region = region

    @property
    def swag_data_file(self):
        return self._swag_data_file

    @swag_data_file.setter
    def swag_data_file(self, swag_data_file):
        self._swag_data_file = swag_data_file

    @property
    def reports_bucket(self):
        return self._reports_bucket

    @reports_bucket.setter
    def reports_bucket(self, reports_bucket):
        self._reports_bucket = reports_bucket

    @property
    def reports_region(self):
        return self._reports_region

    @reports_region.setter
    def reports_region(self, region):
        self._reports_region = region

    @property
    def reports_prefix(self):
        return self._reports_prefix

    @reports_prefix.setter
    def reports_prefix(self, reports_prefix):
        self._reports_prefix = reports_prefix

    @property
    def bucket_snake_role(self):
        return self._bucket_snake_role

    @bucket_snake_role.setter
    def bucket_snake_role(self, role):
        self._bucket_snake_role = role

    @property
    def bucket_snake_session_name(self):
        return self._bucket_snake_session_name

    @bucket_snake_session_name.setter
    def bucket_snake_session_name(self, session_name):
        self._bucket_snake_session_name = session_name


CONFIG = Config()


def load_and_verify_config(func):
    """
    Decorator that sets the attributes on the configuration based on the input to the lambda function (if the env
    var `CONFIG_FROM_INPUT` is set). This will also verify that the configuration is correct and that required
    values are properly configured.

    The values need to be set to the raw values that the configuration needs. For example, if the env var
    would take in a comma-separated-list, you would supply an actual list of the items in the JSON, not the
    comma-separated-string.
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(event, context):
        # Only execute this if the environment variable is set (default should be False)
        if os.environ.get("CONFIG_FROM_INPUT", False):
            if event.get("config"):
                for attribute, value in event["config"].items():
                    if hasattr(CONFIG, attribute):
                        setattr(CONFIG, attribute, value)
                    else:
                        log.error("[X] Config Attribute: {} is not valid.".format(attribute))

        # Verify that all required configuration items have been set:
        for required in CONFIG.required_fields:
            if not getattr(CONFIG, required):
                raise MissingRequiredConfigurationItemException(
                    "Item: {} is required, but not specified.".format(required))

        return func(event, context)

    return wrapper
