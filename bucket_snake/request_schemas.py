"""
.. module: bucket_snake.request_schemas
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
from marshmallow import Schema, fields, validates_schema, ValidationError, validate
from marshmallow.validate import OneOf
from swag_client.backend import SWAGManager
from swag_client.util import parse_swag_config_options

from bucket_snake.config import CONFIG
from bucket_snake.s3.models import BUCKET_TABLE
from bucket_snake.util.exceptions import BlacklistedAccountException, S3BucketDoesNotExistException


def get_swag():
    """
    Get account data from SWAG (via S3)
    :return:
    """
    swag_opts = {
        'swag.type': 's3',
        'swag.bucket_name': CONFIG.swag_bucket,
        'swag.data_file': CONFIG.swag_data_file,
        'swag.region': CONFIG.swag_region,
        'swag.cache_expires': 0
    }
    return SWAGManager(**parse_swag_config_options(swag_opts))


class BucketPermission(Schema):
    """Permission schema for buckets.  Needs a prefix and the corresponding permission"""
    prefix = fields.Str(required=True)
    perms = fields.List(fields.Str(validate=OneOf(["list", "get", "put", "delete"])), required=True)

    @validates_schema
    def validate_prefix(self, data):
        if data.get("prefix") == "":
            raise ValidationError("Prefix cannot be an empty string. Must include a path to something.")

    @validates_schema
    def validate_perms(self, data):
        if not data.get("perms"):
            raise ValidationError("Must include one of the required permissions: list, get, put, delete.")


class BucketDict(fields.Field):
    """The schema for a given bucket. Needs to consist of the bucket name, and a list of the bucket permissions"""
    def __init__(self, bucket_name_field, bucket_permissions_field, *args, **kwargs):
        fields.Field.__init__(self, *args, **kwargs)
        self.bucket_name_field = bucket_name_field
        self.bucket_permissions_field = bucket_permissions_field

    def _deserialize(self, value, attr, data):
        un_serialized_dict = {}

        # K is a string -- The bucket name in the permissions dict
        for k, v in value.items():
            k = self.bucket_name_field.deserialize(k)
            v = self.bucket_permissions_field.deserialize(v)

            # Does this bucket even exist?
            bucket_account = BUCKET_TABLE.buckets.get(k)
            if not bucket_account:
                raise S3BucketDoesNotExistException(k)
            elif bucket_account in CONFIG.blacklisted_bucket_accounts:
                raise BlacklistedAccountException("Bucket: {bucket} resides in blacklisted bucket "
                                                  "account: {account}".format(bucket=k, account=bucket_account))

            un_serialized_dict[k] = v

        return un_serialized_dict


class IncomingRequest(Schema):
    """The main inbound request that arrives from the Lambda launch"""
    role_name = fields.Str(required=True)
    app_name = fields.Str(required=True, validate=[validate.Length(min=1, max=48)])
    account_number = fields.Str(required=True)
    buckets = BucketDict(
        fields.Str(),
        fields.Nested(BucketPermission, many=True)
    )

    @validates_schema
    def validate_account_number(self, data):
        if data.get("account_number"):
            # Make sure the AWS account number exists...
            swag = get_swag()
            result = swag.get("[?id=='{}']".format(data["account_number"]))

            if not result:
                raise ValidationError("Unknown AWS account ID passed in: {}".format(data["account_number"]))

            # Check that the account is not in our blacklisted accounts:
            if data["account_number"] in CONFIG.blacklisted_source_accounts:
                raise BlacklistedAccountException("This tool does NOT service account: {}".format(
                    data["account_number"]))


bucket_permission = BucketPermission(strict=True)
incoming_request = IncomingRequest(strict=True)
