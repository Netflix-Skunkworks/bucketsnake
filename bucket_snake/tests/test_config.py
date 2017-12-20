"""
.. module: bucket_snake.tests.test_config
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import pytest
import os

from bucket_snake.config import Config, load_and_verify_config
from bucket_snake.util.exceptions import MissingRequiredConfigurationItemException


def test_config_required_fields():
    import bucket_snake.config
    old_config = bucket_snake.config.CONFIG
    bucket_snake.config.CONFIG = Config()

    os.environ["CONFIG_FROM_INPUT"] = "true"

    @load_and_verify_config
    def wrapped_func(event, context):
        pass

    # Confirm they are not set:
    for required in bucket_snake.config.CONFIG.required_fields:
        assert not getattr(bucket_snake.config.CONFIG, required)

    # Set them:
    all_required_configs = [
        ("app_reports_buckets", ["reportsbucket", "reportsbucket2"]),
        ("swag_bucket", "swagbucket"),
        ("swag_region", "us-east-1"),
        ("swag_data_file", "v2/accounts.json"),
        ("reports_bucket", "reportsbucket"),
        ("reports_region", "us-east-1")     # Don't set right away...
    ]

    lambda_event = {
        "config": {}
    }

    # Test all but the last...
    for i in range(0, len(all_required_configs) - 1):
        lambda_event["config"][all_required_configs[i][0]] = all_required_configs[i][1]
        with pytest.raises(MissingRequiredConfigurationItemException):
            wrapped_func(lambda_event, None)

    # Should be good:
    lambda_event["config"]["reports_region"] = "us-east-1"
    wrapped_func(lambda_event, None)

    # Are they all set right?
    for config_item, value in all_required_configs:
        assert getattr(bucket_snake.config.CONFIG, config_item) == value

    # Clean-up:
    bucket_snake.config.CONFIG = old_config

    # It should all fail, since the env var is set to not take anything from input:
    os.environ.pop("CONFIG_FROM_INPUT")
    with pytest.raises(MissingRequiredConfigurationItemException):
        wrapped_func(lambda_event, None)
