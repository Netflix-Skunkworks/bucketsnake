"""
.. module: bucket_snake.iam.util
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import json

import boto3
from botocore.exceptions import ClientError

from bucket_snake.config import CONFIG

IAM_CLIENTS = {}


def get_client(arn, technology, region="us-east-1"):
    """
    Generic function to get a boto3 client with the proper assumed role credentials.
    :param arn:
    :param technology:
    :param region:
    :return:
    """
    sts = boto3.client("sts", region_name=region)
    ar = sts.assume_role(RoleArn=arn, RoleSessionName=CONFIG.bucket_snake_session_name)

    session = boto3.Session(
        region_name=region,
        aws_access_key_id=ar["Credentials"]["AccessKeyId"],
        aws_secret_access_key=ar["Credentials"]["SecretAccessKey"],
        aws_session_token=ar["Credentials"]["SessionToken"]
    )

    return session.client(technology)


def format_role_arn(role_name, account_id):
    """
    Gets an IAM ARN string.
    :param role_name:
    :param account_id:
    :return:
    """
    return "arn:aws:iam::{}:role/{}".format(account_id, role_name)


def get_iam_client(account_id):
    """
    Gets a cached IAM client for all the Bucket Snake IAM actions.
    :param account_id:
    :return:
    """
    if IAM_CLIENTS.get(account_id):
        return IAM_CLIENTS[account_id]

    client = get_client(format_role_arn(CONFIG.bucket_snake_role, account_id), "iam", region=CONFIG.iam_region)
    IAM_CLIENTS[account_id] = client

    return client


def check_for_role(role_name, client):
    """
    Checks for an IAM role in a given account
    :param role_name:
    :param client:
    :return:
    """
    try:
        role = client.get_role(RoleName=role_name)

        return role

    except ClientError as ce:
        errors = ["Not Found", "NoSuchEntity"]

        for error in errors:
            if error in str(ce):
                return

        raise ce


def create_iam_role(client, role_name, source_arn, description):
    """
    Creates an IAM role (the S3-specific IAM role for the application), which only permits the
    source application access to assume into it.
    :param client:
    :param role_name:
    :param source_arn:
    :param description:
    :return:
    """
    aspd = {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Principal": {
                    "AWS": source_arn
                }
            }
        ]
    }
    return client.create_role(Path="/", RoleName=role_name,
                              AssumeRolePolicyDocument=json.dumps(aspd, indent=4), Description=description)


def update_aspd(client, role_name, source_arn):
    """
    This updates the existing Assume Role Policy Document for the application's S3-specific IAM role if it already
    exists. This is for idempotence.
    :param client:
    :param role_name:
    :param source_arn:
    :return:
    """
    aspd = {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Principal": {
                    "AWS": source_arn
                }
            }
        ]
    }
    client.update_assume_role_policy(RoleName=role_name, PolicyDocument=json.dumps(aspd, indent=4))
