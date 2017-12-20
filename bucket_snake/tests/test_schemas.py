"""
.. module: bucket_snake.tests.test_schemas
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import json

import pytest
from marshmallow import ValidationError

from bucket_snake.request_schemas import bucket_permission, incoming_request
from bucket_snake.util.exceptions import BlacklistedAccountException, S3BucketDoesNotExistException

BP_ONE = {
    "prefix": "*",
    "perms": [
        "get",
        "put",
        "delete"
    ]
}


def test_bucket_permission_schema():
    bp_one = json.dumps(BP_ONE, sort_keys=True, indent=4)

    bp_two = json.dumps({
        "prefix": "/items/in/this/prefix/*",
        "perms": [
            "get",
            "put",
            "delete"
        ]
    }, sort_keys=True, indent=4)

    bp_three = json.dumps({
        "prefix": "*",
        "perms": ["list"]
    }, sort_keys=True, indent=4)

    # Empty prefix:
    bp_error_one = json.dumps({
        "prefix": "",
        "perms": ["list"]
    }, indent=4)

    # Incorrect permission
    bp_error_two = json.dumps({
        "prefix": "*",
        "perms": [
            "get",
            "list",
            "put",
            "not a permission"
        ]
    }, indent=4)

    # Incorrect data type:
    bp_error_three = json.dumps({
        "prefix": True,
        "perms": [
            "get",
            "list",
            "put",
            "not a permission"
        ]
    }, indent=4)

    # Missing permission:
    bp_error_four = json.dumps({
        "prefix": "*",
        "perms": []
    }, indent=4)

    assert json.dumps(bucket_permission.loads(bp_one).data, sort_keys=True, indent=4) == bp_one
    assert json.dumps(bucket_permission.loads(bp_two).data, sort_keys=True, indent=4) == bp_two
    assert json.dumps(bucket_permission.loads(bp_three).data, sort_keys=True, indent=4) == bp_three

    with pytest.raises(ValidationError):
        bucket_permission.loads(bp_error_one)

    with pytest.raises(ValidationError):
        bucket_permission.loads(bp_error_two)

    with pytest.raises(ValidationError):
        bucket_permission.loads(bp_error_three)

    with pytest.raises(ValidationError):
        bucket_permission.loads(bp_error_four)


def test_incoming_request_schema(bucket_table):
    request_one = json.dumps({
        "role_name": "BucketSnakeLambdaProfile",
        "app_name": "BucketSnake",
        "account_number": "012345678910",
        "buckets": {
            "test-bucket-one": [
                BP_ONE
            ]
        }
    }, sort_keys=True, indent=4)

    # With an invalid permission:
    request_err = json.dumps({
        "role_name": "BucketSnakeLambdaProfile",
        "app_name": "BucketSnake",
        "account_number": "012345678910",
        "buckets": {
            "test-bucket-one": [
                {
                    "prefix": "",
                    "perms": ["list"]
                }
            ]
        }
    }, indent=4)

    # With an account we don't have:
    request_err_two = json.dumps({
        "role_name": "BucketSnakeLambdaProfile",
        "app_name": "BucketSnake",
        "account_number": "333333333333",
        "buckets": {
            "test-bucket-one": [
                BP_ONE
            ]
        }
    }, indent=4)

    # With an app name that is more than 48 characters:
    request_err_three = json.dumps({
        "role_name": "BucketSnakeLambdaProfile",
        "app_name": "x" * 49,
        "account_number": "012345678910",
        "buckets": {
            "test-bucket-one": [
                BP_ONE
            ]
        }
    }, indent=4)

    # With a blacklisted account:
    blacklisted = json.dumps({
        "role_name": "BucketSnakeLambdaProfile",
        "app_name": "BucketSnake",
        "account_number": "666666666666",
        "buckets": {
            "test-bucket-one": [
                BP_ONE
            ]
        }
    }, sort_keys=True, indent=4)

    # With a bucket in a blacklisted account:
    blacklisted_bucket = json.dumps({
        "role_name": "BucketSnakeLambdaProfile",
        "app_name": "BucketSnake",
        "account_number": "012345678910",
        "buckets": {
            "blacklisted-bucket-one": [
                BP_ONE
            ],

        }
    }, sort_keys=True, indent=4)

    # With a bucket that doesn't exist:
    nonexisting_bucket = json.dumps({
        "role_name": "BucketSnakeLambdaProfile",
        "app_name": "BucketSnake",
        "account_number": "012345678910",
        "buckets": {
            "not-a-bucket": [
                BP_ONE
            ],

        }
    }, sort_keys=True, indent=4)

    assert json.dumps(incoming_request.loads(request_one).data, sort_keys=True, indent=4) == request_one

    with pytest.raises(ValidationError):
        incoming_request.loads(request_err)

    with pytest.raises(ValidationError):
        incoming_request.loads(request_err_two)

    with pytest.raises(ValidationError):
        incoming_request.loads(request_err_three)

    with pytest.raises(ValidationError):
        incoming_request.loads(blacklisted)

    with pytest.raises(BlacklistedAccountException):
        incoming_request.loads(blacklisted_bucket)

    with pytest.raises(S3BucketDoesNotExistException):
        incoming_request.loads(nonexisting_bucket)
