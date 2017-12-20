"""
.. module: bucket_snake.entrypoints
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
import logging
import os

from marshmallow import ValidationError
from raven_python_lambda import RavenLambdaWrapper

from bucket_snake.config import load_and_verify_config
from bucket_snake.iam.logic import update_instance_profile_s3_permissions, create_destination_roles, \
    update_source_assume_role_policy
from bucket_snake.iam.util import get_iam_client, check_for_role
from bucket_snake.request_schemas import incoming_request
from bucket_snake.s3.models import BUCKET_TABLE
from bucket_snake.s3.permissions import build_bucket_account_mapping, collect_policies, create_s3_role_policies, \
    create_access_to_reports
from bucket_snake.util.exceptions import InvalidRequestException, SourceRoleDoesNotExistException

logging.basicConfig()
log = logging.getLogger("bucket_snake")
log.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))


def validate_request(payload):
    """
    This will validate that the payload contains the proper S3 permissions via Marshmallow
    :param payload:
    :return:
    """
    try:
        request_data = incoming_request.load(payload).data

    except ValidationError as ve:
        log.debug("[X] Invalid properties sent in. Here is the specific error details:")
        raise InvalidRequestException("Invalid data was sent in through the payload. See: {}".format(str(ve)))

    return request_data


def main_logic(request_data):
    """
    The main logic for the Lambda. This assumes that the input request has been properly validated.
    This means that all buckets requested exist and are properly permissible.
    :param request_data:
    :return:
    """
    # STEP 1: VERIFY THAT SOURCE IAM ROLES EXISTS #
    log.debug("[~] Checking if the source IAM role: {} exists in {}...".format(request_data["role_name"],
                                                                                 request_data["account_number"]))
    iam_client = get_iam_client(request_data["account_number"])
    if not check_for_role(request_data["role_name"], iam_client):
        log.debug("[X] Source IAM role does NOT exist. That must be created first before this lambda is called.")
        raise SourceRoleDoesNotExistException("Source IAM Role: {} does not exist. This must exist before running "
                                              "this script.".format(request_data["role_name"]))

    # STEP 2: BUILD THE S3 PERMISSIONS MATRIX #
    # Need to determine which buckets are in the same account, and which are not
    log.debug("[~] Building the account->bucket mapping...")
    buckets_same, buckets_cross = build_bucket_account_mapping(request_data)
    log.debug("[+] Completed the account->bucket mapping.")

    # Calculate the S3 permissions that are required:
    log.debug("[~] Calculating the same account S3 permissions required...")
    policies_same_account = create_s3_role_policies(collect_policies(buckets_same))
    log.debug("[+] Completed calculation of same account S3 permissions.")

    log.debug("[~] Determining the permissions for access to the historical S3 reports...")
    create_access_to_reports(policies_same_account, request_data["account_number"])
    log.debug("[+] Completed calculation of permissions for historical S3 reports.")

    log.debug("[~] Calculating the cross-account S3 permissions required...")
    policies_cross_account = create_s3_role_policies(collect_policies(buckets_cross))
    log.debug("[+] Completed calculation of cross-account S3 permissions.")

    # STEP 3: CREATE ROLES AND GRANT THE PERMISSIONS #
    # Grant the same-account access:
    log.debug("[~] Updating the source role ({source_role})'s S3 permissions "
              "(in account: {source_account})...".format(source_role=request_data["app_name"],
                                                         source_account=request_data["account_number"]))
    update_instance_profile_s3_permissions(policies_same_account, request_data["app_name"],
                                           request_data["role_name"], request_data["account_number"])
    log.debug("[+] Updated the source role ({})'s S3 Permissions.".format(request_data["app_name"]))

    # Create the cross-account roles:
    log.debug("[~] Creating the destination roles...")
    create_destination_roles(policies_cross_account, request_data["app_name"],
                             request_data["role_name"], request_data["account_number"])
    log.debug("[+] Completed destination role creation...")

    # Update the assume role permissions:
    log.debug("[~] Updating the source role's role assumption permissions...")
    update_source_assume_role_policy(policies_cross_account, request_data["app_name"],
                                     request_data["role_name"], request_data["account_number"])
    log.debug("[+] Completed updating the source role's role assumption permissions...")

    # DONE!
    log.info("[+] Permissionsss fixed for sssource role: {source}, app: {app}, account: {account}!".format(
        source=request_data["role_name"], app=request_data["app_name"], account=request_data["account_number"]
    ))


@RavenLambdaWrapper()
@load_and_verify_config
def handler(event, context):
    """
    The main Lambda entrypoint. Validates that all is well before continuing on.
    :param event:
    :param context:
    :return:
    """
    log.debug("[~] SSSSSSSSSSSSSSsssssssSSSSSSSSSS")

    # Set up the config first:
    # set_config_from_input(event)

    # Fetch the Historical S3 Reports data
    _ = BUCKET_TABLE.buckets

    # Parse and validate that the payload is correct:
    log.debug("[~] Parsing request data...")
    request_data = validate_request(event)
    log.debug("[+] Successfully loaded incoming request data.")

    # Continue:
    main_logic(request_data)
    log.debug("[+] Function complete")
