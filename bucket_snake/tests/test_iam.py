"""
.. module: bucket_snake.tests.test_iam
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import bucket_snake.iam.util

from bucket_snake.config import CONFIG
from bucket_snake.iam.logic import create_destination_roles, update_instance_profile_s3_permissions, \
    update_source_assume_role_policy
from bucket_snake.iam.util import get_client, format_role_arn, get_iam_client, check_for_role, create_iam_role, \
    update_aspd
from bucket_snake.s3.permissions import create_s3_role_policies, collect_policies


def test_get_client(sts, config):
    client = get_client(format_role_arn(CONFIG.bucket_snake_role, "012345678910"), "iam")

    assert client


def test_get_iam_client(sts, config, iam_client_dict):
    client = get_iam_client("012345678910")

    assert client
    assert bucket_snake.iam.util.IAM_CLIENTS["012345678910"] == client

    client = get_iam_client("012345678910")
    assert bucket_snake.iam.util.IAM_CLIENTS["012345678910"] == client
    assert len(bucket_snake.iam.util.IAM_CLIENTS) == 1


def test_check_for_role(iam, existing_role):
    assert check_for_role("someAppInstanceProfile", iam)
    assert not check_for_role("Idontexist", iam)


def test_create_iam_role(iam, config):
    created_role = create_iam_role(iam, "destRole",
                                   format_role_arn("sourceRole", "012345678910"),
                                   CONFIG.dest_role_description)
    assert created_role
    assert created_role["Role"]["RoleName"] == "destRole"
    assert len(created_role["Role"]["AssumeRolePolicyDocument"]["Statement"]) == 1
    assert \
        created_role["Role"]["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]["AWS"] == \
        format_role_arn("sourceRole", "012345678910")


def test_update_aspd(iam, existing_role):
    update_aspd(iam, "someAppInstanceProfile", format_role_arn("sourceRole", "012345678910"))
    updated_role = iam.get_role(RoleName="someAppInstanceProfile")

    assert \
        updated_role["Role"]["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]["AWS"] == \
        format_role_arn("sourceRole", "012345678910")


def test_create_destination_roles(iam, sts, config, buckets_cross_account_mapping):
    role_policies = create_s3_role_policies(collect_policies(buckets_cross_account_mapping))
    create_destination_roles(role_policies, "someApp", "someAppInstanceProfile", "012345678910")

    # Verify:
    role = iam.get_role(RoleName="someApp-012345678910")
    assert role
    assert role["Role"]["AssumeRolePolicyDocument"]["Statement"][0] \
               ["Principal"]["AWS"] == format_role_arn("someAppInstanceProfile", "012345678910")

    policies = iam.get_role_policy(RoleName="someApp-012345678910",
                                   PolicyName=CONFIG.bucket_snake_policy_name)

    assert len(policies["PolicyDocument"]["Statement"]) == 2


def test_update_instance_profile_s3_permissions(iam, sts, existing_role, buckets_same_account_mapping, config):
    role_policies = create_s3_role_policies(collect_policies(buckets_same_account_mapping))

    update_instance_profile_s3_permissions(role_policies, "someApp", "someAppInstanceProfile", "012345678910")

    # Verify:
    policies = iam.get_role_policy(RoleName="someAppInstanceProfile",
                                   PolicyName=CONFIG.bucket_snake_policy_name)

    assert len(policies["PolicyDocument"]["Statement"]) == 4


def test_update_source_assume_role_policy(iam, sts, existing_role, config, buckets_cross_account_mapping):
    role_policies = create_s3_role_policies(collect_policies(buckets_cross_account_mapping))

    update_source_assume_role_policy(role_policies, "someApp", "someAppInstanceProfile", "012345678910")

    # Verify:
    policies = iam.get_role_policy(RoleName="someAppInstanceProfile",
                                   PolicyName=CONFIG.sts_policy_name)

    assert len(policies["PolicyDocument"]["Statement"]) == 1
    assert policies["PolicyDocument"]["Statement"][0]["Resource"][0] == "arn:aws:iam::012345678911" \
                                                                        ":role/someApp-012345678910"
