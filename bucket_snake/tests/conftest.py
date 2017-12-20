"""
.. module: bucket_snake.tests.conftest
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import json
import os

import boto3
import pytest
from moto import mock_sts, mock_iam, mock_s3, mock_sns

import bucket_snake.iam.util
import bucket_snake.config
from bucket_snake.config import CONFIG
from bucket_snake.tests.conf import SWAG_BUCKET, HISTORICAL_REPORT_BUCKET, EXISTING_ASPD
import bucket_snake.s3.models
from bucket_snake.s3.models import BUCKET_TABLE, BucketTable


class MockContext:
    @staticmethod
    def get_remaining_time_in_millis():
        return 9000


def get_json(file):
    cwd = os.path.dirname(os.path.realpath(__file__))
    object_path = os.path.join(cwd, 'templates/{}'.format(file))

    with open(object_path, 'r') as op:
        return op.read()


@pytest.yield_fixture(scope="function")
def sts():
    mock_sts().start()

    client = boto3.client("sts")

    yield client

    mock_sts().stop()


@pytest.yield_fixture(scope="function")
def sns():
    mock_sns().start()

    client = boto3.client("sns", region_name="us-west-2")

    yield client

    mock_sns().stop()


@pytest.yield_fixture(scope="function")
def iam():
    mock_iam().start()

    client = boto3.client("iam")

    yield client

    mock_iam().stop()


@pytest.yield_fixture(scope="function")
def s3():
    mock_s3().start()

    client = boto3.client("s3", region_name="us-west-2")

    yield client

    mock_s3().stop()


@pytest.yield_fixture(scope="function")
def config():
    old_config = bucket_snake.config.CONFIG
    CONFIG.app_reports_buckets = [HISTORICAL_REPORT_BUCKET]
    CONFIG.swag_region = "us-west-2"
    CONFIG.swag_data_file = "accounts.json"
    CONFIG.swag_bucket = SWAG_BUCKET
    CONFIG.reports_bucket = HISTORICAL_REPORT_BUCKET
    CONFIG.reports_region = "us-west-2"
    CONFIG.blacklisted_source_accounts = ["666666666666", "000000000000"]
    CONFIG.blacklisted_bucket_accounts = ["989898989898", "898989898989", "666666666666"]

    yield

    bucket_snake.config.CONFIG = old_config


@pytest.yield_fixture(scope="function")
def iam_client_dict():
    yield
    bucket_snake.iam.util.IAM_CLIENTS = {}


@pytest.yield_fixture(scope="function")
def buckets(s3):
    s3.create_bucket(Bucket=SWAG_BUCKET)
    s3.create_bucket(Bucket=HISTORICAL_REPORT_BUCKET)

    bucket_keys = [
        (SWAG_BUCKET, "accounts.json"),
        (HISTORICAL_REPORT_BUCKET, "historical-s3-report.json")
    ]

    for bucket, key in bucket_keys:
        s3.put_object(Bucket=bucket, Key=key, Body=get_json(key))


@pytest.yield_fixture(scope="function")
def bucket_table(buckets, config):
    old_bucket_table = bucket_snake.s3.models.BUCKET_TABLE
    bucket_snake.s3.models.BUCKET_TABLE = BucketTable()

    yield BUCKET_TABLE.buckets

    bucket_snake.s3.models.BUCKET_TABLE = old_bucket_table


@pytest.fixture(scope="function")
def existing_role(iam):
    iam.create_role(Path="/", RoleName="someAppInstanceProfile",
                    AssumeRolePolicyDocument=json.dumps(EXISTING_ASPD))

    return iam


@pytest.fixture(scope="function")
def s3_role_event():
    return {
        "role_name": "someAppInstanceProfile",
        "app_name": "someApp",
        "account_number": "012345678910",
        "buckets": {
            "test-bucket-one": [
                {
                    "prefix": "*",
                    "perms": [
                        "list"
                    ]
                },
                {
                    "prefix": "some/path/*",
                    "perms": [
                        "get",
                        "put",
                        "delete"
                    ]
                }
            ],
            "test-bucket-two": [
                {
                    "prefix": "*",
                    "perms": [
                        "list",
                        "get"
                    ]
                }
            ],
            "test-bucket-three": [
                {
                    "prefix": "*",
                    "perms": [
                        "list"
                    ]
                },
                {
                    "prefix": "*",
                    "perms": [
                        "get"
                    ]
                }
            ],
            "test-bucket-four": [
                {
                    "prefix": "*",
                    "perms": [
                        "list",
                        "get"
                    ]
                }
            ],
        }
    }


@pytest.fixture(scope="function")
def buckets_same_account_mapping():
    return {
        "test-bucket-one": {
            "permissions": [
                {
                    "prefix": "*",
                    "perms": [
                        "list"
                    ]
                },
                {
                    "prefix": "some/path/*",
                    "perms": [
                        "get",
                        "put",
                        "delete"
                    ]
                }
            ],
            "account_number": "012345678910"
        },
        "test-bucket-two": {
            "permissions": [
                {
                    "prefix": "*",
                    "perms": [
                        "list",
                        "get"
                    ]
                }
            ],
            "account_number": "012345678910"
        }
    }


@pytest.fixture(scope="function")
def buckets_cross_account_mapping():
    return {
        "test-bucket-three": {
            "permissions": [
                {
                    "prefix": "*",
                    "perms": [
                        "list"
                    ]
                },
                {
                    "prefix": "*",
                    "perms": [
                        "get"
                    ]
                }
            ],
            "account_number": "012345678911"
        },
        "test-bucket-four": {
            "permissions": [
                {
                    "prefix": "*",
                    "perms": [
                        "list",
                        "get"
                    ]
                }
            ],
            "account_number": "012345678911"
        }
    }


@pytest.fixture(scope="function")
def mock_lambda_context():
    return MockContext()
