"""
.. module: bucket_snake.iam.logic
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import json
import logging
import os

from bucket_snake.config import CONFIG
from bucket_snake.iam.util import get_iam_client, check_for_role, create_iam_role, format_role_arn, update_aspd

logging.basicConfig()
log = logging.getLogger("bucket_snake")
log.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


def create_destination_roles(bucket_policies, app_name, source_role, source_role_account):
    """
    This will create the destination IAM roles for which the source application can assume into.
    These roles only permit S3 access.
    :param bucket_policies:
    :param app_name:
    :param source_role:
    :param source_role_account:
    :return:
    """
    for account, policies in bucket_policies.items():
        client = get_iam_client(account)

        # Check if the destination role exists:
        destination_role_name = "{app}-{account}".format(app=app_name, account=source_role_account)

        log.debug("\t[ ] Checking for destination role in {}...".format(account))

        if not check_for_role(destination_role_name, client):
            log.debug("\t[@] Destination role does not exist... Creating...")
            # Create the role:
            create_iam_role(client, destination_role_name,
                            format_role_arn(source_role, source_role_account),
                            CONFIG.dest_role_description)

            log.debug("\t[+] Created the destination role in account {}".format(account))

        else:
            log.debug("\t[ ] Updating the ASPD of the role in account {}...".format(account))
            update_aspd(client, destination_role_name, format_role_arn(source_role, source_role_account))

        log.debug("\t[ ] Updating the role policy...")
        client.put_role_policy(RoleName=destination_role_name, PolicyName=CONFIG.bucket_snake_policy_name,
                               PolicyDocument=json.dumps(policies, indent=4, sort_keys=True))
        log.debug("\t[+] Updated the role policy in account {}".format(account))


def update_instance_profile_s3_permissions(bucket_policies, app_name, source_role, source_role_account):
    """
    This will grant the source application access to S3. This avoids having to assume role within the same
    AWS account.
    :param bucket_policies:
    :param app_name:
    :param source_role:
    :param source_role_account:
    :return:
    """
    if bucket_policies.get(source_role_account):
        client = get_iam_client(source_role_account)

        client.put_role_policy(RoleName=source_role, PolicyName=CONFIG.bucket_snake_policy_name,
                               PolicyDocument=json.dumps(bucket_policies[source_role_account], indent=4,
                                                         sort_keys=True))


def update_source_assume_role_policy(cross_account_policies, app_name, source_role, source_account):
    """
    This permits the source application the ability to assume into the destination S3 roles.
    :param cross_account_policies:
    :param app_name:
    :param source_role:
    :param source_account:
    :return:
    """
    assume_role_perm = {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": []
            }
        ]
    }

    client = get_iam_client(source_account)

    for account in cross_account_policies.keys():
        destination_role_name = "{app}-{account}".format(app=app_name, account=source_account)

        # Is this where we should do the diff logic for old role cleanup?
        assume_role_perm["Statement"][0]["Resource"].append(
            format_role_arn(destination_role_name, account)
        )

    client.put_role_policy(RoleName=source_role, PolicyName=CONFIG.sts_policy_name,
                           PolicyDocument=json.dumps(assume_role_perm, indent=4, sort_keys=True))
