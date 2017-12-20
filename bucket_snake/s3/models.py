"""
.. module: bucket_snake.s3.models
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import logging
import os

import boto3
from marshmallow import Schema
from marshmallow.fields import Field
from retrying import retry

from bucket_snake.config import CONFIG

logging.basicConfig()
log = logging.getLogger("bucket_snake")
log.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


class BucketField(Field):
    """Field for the bucket dictionary. It's `bucket_name: bucket_account`"""
    def _deserialize(self, value, attr, data):
        return {name: details["AccountId"] for name, details in data["buckets"].items()}


class S3ReportSchema(Schema):
    """Schema for the S3 Historical report, which only cares about the buckets."""
    buckets = BucketField(required=True, load_from="buckets", load_only=True)


class BucketTable:
    """
    Class that fetches the Historical S3 Table and stores it for later use.

    To use: `from bucket_snake.s3.models import BUCKET_TABLE`
    Then, `BUCKET_TABLE.buckets["bucket_name"]` to get the account that the bucket resides in
    """
    def __init__(self):
        self._buckets = None

    @property
    def buckets(self):
        if not self._buckets:
            self._buckets = BucketTable.__get_bucket_table()

        return self._buckets

    @staticmethod
    def __get_bucket_table():
        """
        Fetches the Historical S3 data, and gets back the dictionary mapping of Bucket -> Account
        :return:
        """
        log.debug("[~] Fetching the Historical S3 report data for deserialization...")

        report = BucketTable.__fetch_from_s3()

        return S3ReportSchema(strict=True).loads(report).data["buckets"]

    @staticmethod
    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def __fetch_from_s3():
        """
        Fetches the Historical reports data from S3
        :return:
        """
        log.debug("[~] Fetching Historical S3 Report...")
        client = boto3.client("s3", region_name=CONFIG.reports_region)

        s3_obj = client.get_object(Bucket=CONFIG.reports_bucket, Key=CONFIG.reports_prefix)
        log.debug("[+] Successfully fetched Historical S3 Report...")

        return s3_obj["Body"].read().decode()


# Use this for all S3 Historical Bucket related data:
BUCKET_TABLE = BucketTable()
