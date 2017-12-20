"""
.. module: bucket_snake.tests.test_fixtures
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import json

from bucket_snake.tests.conf import SWAG_BUCKET, HISTORICAL_REPORT_BUCKET
from bucket_snake.tests.conftest import get_json
from bucket_snake.config import CONFIG


def test_buckets(s3, buckets):
    bucket_keys = [
        (SWAG_BUCKET, "accounts.json"),
        (HISTORICAL_REPORT_BUCKET, "historical-s3-report.json")
    ]

    for bucket, key in bucket_keys:
        obj = s3.get_object(Bucket=bucket, Key=key)
        s3_json = json.loads(obj["Body"].read().decode("utf-8"))
        template_json = json.loads(get_json(key))

        # Assures that no formatting and tabbing differences exist:
        assert json.dumps(s3_json, indent=4) == json.dumps(template_json, indent=4)


def test_bucket_table(bucket_table):
    assert len(bucket_table) == 6

    mapping = [
        ("test-bucket-one", "012345678910"),
        ("test-bucket-two", "012345678910"),
        ("test-bucket-three", "012345678911"),
        ("test-bucket-four", "012345678911"),
        ("blacklisted-bucket-one", "666666666666"),
        ("blacklisted-bucket-two", "000000000000")
    ]

    for name, account in mapping:
        assert bucket_table[name] == account


def test_config(config):
    assert CONFIG.swag_region == "us-west-2"
    assert CONFIG.swag_data_file == "accounts.json"
    assert CONFIG.swag_bucket == SWAG_BUCKET
    assert CONFIG.reports_bucket == HISTORICAL_REPORT_BUCKET
    assert CONFIG.reports_region == "us-west-2"

    for bl in ["666666666666", "000000000000"]:
        assert bl in CONFIG.blacklisted_source_accounts

    for bl in ["989898989898", "898989898989", "666666666666"]:
        assert bl in CONFIG.blacklisted_bucket_accounts
