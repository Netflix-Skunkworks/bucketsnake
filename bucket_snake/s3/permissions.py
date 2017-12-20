"""
.. module: bucket_snake.s3.permissions
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
from bucket_snake.s3.models import BUCKET_TABLE
from bucket_snake.config import CONFIG

# This is the main lookup table for general access types (list, get, put, delete), and the corresponding
# AWS S3 permissions required to grant:
S3_PERMISSIONS = {
    "list": [
        "s3:ListBucket",
        "s3:ListBucketVersions"
    ],
    "get": [
        "s3:GetObject",
        "s3:GetObjectTagging",
        "s3:GetObjectVersion",
        "s3:GetObjectVersionTagging",
        "s3:GetObjectAcl",
        "s3:GetObjectVersionAcl"
    ],
    "put": [
        "s3:PutObject",
        "s3:PutObjectTagging",
        "s3:PutObjectVersionTagging",
        "s3:ListMultipartUploadParts*",
        "s3:AbortMultipartUpload",
        "s3:RestoreObject"
    ],
    "delete": [
        "s3:DeleteObject",
        "s3:DeleteObjectTagging",
        "s3:DeleteObjectVersion",
        "s3:DeleteObjectVersionTagging"
    ]
}


def check_if_cross_account(source_account_number, bucket):
    """Determine if the bucket resides in a different account than the source account"""
    if BUCKET_TABLE.buckets[bucket] == source_account_number:
        return False

    return True


def build_bucket_account_mapping(request_data):
    """
    This will build a mapping and return two dicts, one with all buckets in the same account as the source
    application, and the other with all the cross-account S3 buckets.
    :param request_data:
    :return:
    """
    buckets_same_account = {}
    buckets_cross_account = {}

    for bucket, permissions in request_data["buckets"].items():
        # Determine which account the given bucket is in:
        if check_if_cross_account(request_data["account_number"], bucket):
            buckets_cross_account[bucket] = dict(permissions=permissions,
                                                 account_number=BUCKET_TABLE.buckets[bucket])
        else:
            buckets_same_account[bucket] = dict(permissions=permissions,
                                                account_number=request_data["account_number"])

    return buckets_same_account, buckets_cross_account


def collect_policies(buckets_dict):
    """
    This creates the mapping of AWS S3 IAM permissions for a given AWS account (for where the bucket resides)
    :param buckets_dict:
    :return:
    """
    account_policies = {}

    for bucket, details in buckets_dict.items():
        policy = account_policies.get(details["account_number"], {
            "list": set(),
            "get": set(),
            "put": set(),
            "delete": set()
        })

        for prefix_perms in details["permissions"]:
            for perm in prefix_perms["perms"]:
                bucket_arn = "arn:aws:s3:::{bucket}".format(bucket=bucket)

                # LIST permissions apply to the whole bucket:
                if perm == "list":
                    policy["list"].add(bucket_arn)

                else:
                    prefix_arn = "{bucket_arn}/{prefix}".format(bucket_arn=bucket_arn, prefix=prefix_perms["prefix"])
                    policy[perm].add(prefix_arn)

        # Update the policy for the account:
        account_policies[details["account_number"]] = policy

    return account_policies


def create_s3_role_policies(collected_policies):
    """
    This creates the IAM template with the permissions from the mapping created in `collect_policies`.
    :param collected_policies:
    :return:
    """
    account_iam_policies = {}

    for account, policies in collected_policies.items():
        statements = []

        for perm, arns in policies.items():
            # Skip empty permissions:
            if len(arns) == 0:
                continue

            statements.append({
                "Sid": perm.title(),
                "Effect": "Allow",
                "Action": S3_PERMISSIONS[perm],
                "Resource": list(arns)
            })

        account_iam_policies[account] = {
            "Statement": statements
        }

    return account_iam_policies


def create_access_to_reports(account_iam_policies, app_account):
    """
    This creates the permissions required for the application to read from the historical reports bucket.
    This is so the application can access the S3 dictionary to determine if role assumption is required or not.

    The buckets that the application will access are defined in the Config's `app_reports_buckets` list.
    The application will not assume to any role to access this -- this will be cross-account access, so
    the bucket policy needs to be there.
    :return:
    """
    if not account_iam_policies.get(app_account):
        account_iam_policies[app_account] = {"Statement": []}

    resources = ["arn:aws:s3:::{b}/{p}".format(b=b, p=CONFIG.reports_prefix) for b in CONFIG.app_reports_buckets]

    account_iam_policies[app_account]["Statement"].append({
        "Sid": "HistoricalS3Reports",
        "Effect": "Allow",
        "Action": "s3:GetObject",
        "Resource": resources
    })
