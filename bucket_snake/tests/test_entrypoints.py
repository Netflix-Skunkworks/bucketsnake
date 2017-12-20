"""
.. module: bucket_snake.tests.test_entrypoints
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import pytest

import bucket_snake.iam.util
from bucket_snake.config import CONFIG
from bucket_snake.entrypoints import handler
from bucket_snake.util.exceptions import SourceRoleDoesNotExistException


def test_create_successful(s3_role_event, existing_role, sts, config, buckets, mock_lambda_context, iam_client_dict):
    bucket_snake.iam.util.IAM_CLIENTS["012345678910"] = existing_role

    handler(s3_role_event, mock_lambda_context)

    # Check that the "BucketSnake" and "BucketSnakeAssumeRole" policies were added to the application's role:
    policy_names = existing_role.list_role_policies(RoleName="someAppInstanceProfile")
    assert len(policy_names["PolicyNames"]) == 2
    assert "BucketSnake" in policy_names["PolicyNames"]
    assert "BucketSnakeAssumeRole" in policy_names["PolicyNames"]

    policies = existing_role.get_role_policy(RoleName="someAppInstanceProfile",
                                             PolicyName=CONFIG.sts_policy_name)
    assert len(policies["PolicyDocument"]["Statement"]) == 1
    assert policies["PolicyDocument"]["Statement"][0]["Action"] == "sts:AssumeRole"
    assert len(policies["PolicyDocument"]["Statement"][0]["Resource"]) == 1
    assert policies["PolicyDocument"]["Statement"][0]["Resource"][0] == "arn:aws:iam::012345678911:role/someApp" \
                                                                        "-012345678910"

    policies = existing_role.get_role_policy(RoleName="someAppInstanceProfile",
                                             PolicyName=CONFIG.bucket_snake_policy_name)
    assert len(policies["PolicyDocument"]["Statement"]) == 5

    # Check that the last policy added is the Historical S3 Reports policy:
    assert policies["PolicyDocument"]["Statement"][4]["Sid"] == "HistoricalS3Reports"
    assert policies["PolicyDocument"]["Statement"][4]["Effect"] == "Allow"
    assert policies["PolicyDocument"]["Statement"][4]["Action"] == "s3:GetObject"
    assert policies["PolicyDocument"]["Statement"][4]["Resource"] == \
        ["arn:aws:s3:::historical-reports/historical-s3-report.json"]

    # Cross Account:
    policy_names = bucket_snake.iam.util.IAM_CLIENTS["012345678911"].list_role_policies(RoleName="someApp-012345678910")
    assert len(policy_names["PolicyNames"]) == 1
    assert policy_names["PolicyNames"][0] == "BucketSnake"

    policies = bucket_snake.iam.util.IAM_CLIENTS["012345678911"].get_role_policy(RoleName="someApp-012345678910",
                                                                                 PolicyName="BucketSnake")
    assert len(policies["PolicyDocument"]["Statement"]) == 2

    aspd = bucket_snake.iam.util.IAM_CLIENTS["012345678911"].get_role(RoleName="someApp-012345678910")
    assert len(aspd["Role"]["AssumeRolePolicyDocument"]["Statement"]) == 1
    assert aspd["Role"]["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]["AWS"] == "arn:aws:iam::012345678910" \
                                                                                           ":role/someAppInstance" \
                                                                                           "Profile"


def test_without_existing_role(s3_role_event, sts, iam, config, buckets, mock_lambda_context, iam_client_dict):
    with pytest.raises(SourceRoleDoesNotExistException):
        handler(s3_role_event, mock_lambda_context)
