---
id: howitworks
title: How Bucket Snake Works
sidebar_label: How it works
---

Bucket Snake works by creating and provisioning IAM roles in the accounts that own buckets for a given application.

The general flow works as follows:
1. Bucket Snake gets triggered with a payload describing:
    - The name of the application
    - The IAM role name that application uses
    - The AWS account the application's IAM role resides in.
    - A set of S3 buckets, and the corresponding permissions to grant
1. With the above information, Bucket Snake figures out where the buckets are located, creates the necessary roles with the access requested.
    - If an S3 bucket resides in the same account as the source application, Bucket Snake simply grants permissions to the source application, so no role assumption is required.

## Sources of Truth
Bucket Snake depends on [SWAG](https://github.com/Netflix-Skunkworks/swag-api), [Historical](https://github.com/Netflix-Skunkworks/historical), and the [Historical S3 Report](https://github.com/Netflix-Skunkworks/historical-reports).

SWAG is a schema for the accounts in your infrastructure. It's a source of truth to know which AWS accounts you have, and some details about them.

Historical keeps track of all S3 buckets in your infrastructure, and the Historical S3 Report is a JSON file that is a dump of all S3 buckets currently in your infrastructure. This is used as a lookup-table to know which buckets you have, which region and AWS account they reside in.

### Historical Reports
The historical s3 report is needed because S3 ARNs don't provide enough detail on S3 buckets. For example, one cannot determine the account and region by just having an S3 ARN or bucket name.

The Historical S3 report solves this by providing a look-up table of S3 bucket, and the corresponding region and AWS account for the bucket. This is what Bucket Snake uses to determine if S3 access is cross-account.

A Bucket Snake aware client needs access to this data source to determine if role-assumption is required. It is assumed that this report is stored in an S3 bucket that permits multiple accounts in your infrastructure access to it (on the bucket policy). Bucket Snake will grant the application access to this JSON file.

## Triggering the Lambda
Bucket Snake is triggered from an AWS lambda function invocation that has a payload with this schema:

    {
        "role_name": "AppSourceIamRole",
        "app_name": "nameOfAppWithSourceIAMRole",
        "account_number": "The12digitAWSAccountIDWhereTheAppSourceIAMRoleLives",
        "buckets": {
            "name-of-s3-bucket": [
                {
                    "prefix": "*",
                    "perms": [
                        "list"
                    ]
                },
                {
                    "prefix": "some/prefix/here",
                    "perms": [
                        "get",
                        "put",
                        "delete"
                    ]
                }
            ]
            "another-s3-bucket": [
                "perms": [
                    "get"
                ],
                "prefix: "*"
            ],
            "and-another-s3-bucket": [
                "perms": [
                    "put"
                ],
                "prefix": "some/drop/location"
            ],
            ...
        }
    }


### Now what?
Bucket Snake would receive the JSON from the lambda invocation, and from that, would:
1. Verify that the source IAM role exists
1. Verify that the buckets exist, and are permitted by Bucket Snake (more on this in the configuration section)
1. Determine which S3 buckets are in the same account as the source application, and which are not
1. For buckets in the same account, Bucket Snake will add in the proper S3 permissions to the source app IAM role
1. For buckets that are not in the same account, Bucket Snake will create IAM roles in the destination accounts with access to the respective buckets
    - Destination IAM role name follows the format: `AppName-12DigitSourceAccountNumber`.
    - This role will have a trust policy that allows the source application `sts:AssumeRole` access to it.
1. If applicable, a policy will be added to the source IAM role to grant `sts:AssumeRole` access to those destination
   IAM roles
1. And lastly, Bucket Snake will grant access to the Historical S3 report's JSON file so that application knows
   which S3 buckets require the role assumption for access.

## How does my application make use of this?
At present no "Bucket Snake aware" client library exists. We are currently in the process of developing one for Python and Java.

This client would work by:
1. Fetch the Historical S3 JSON (access granted by Bucket Snake)
1. Check if the S3 bucket is in the same account (this information lives in the Historical report).

If it's in the same account, then the client directly access the bucket with the on-instance
IAM credentials.

If the bucket is in a _different account_:
1. Assume to the destination role (named `AppName-12DigitSourceAccountNumber`),
1. Cache the credentials for future use (re-assume when expired)
1. Use the assumed credentials to access the S3 bucket

## What about future access?
Simply pass in a new payload to the lambda with additional buckets to add access to. Bucket Snake is [idempotent](https://en.wikipedia.org/wiki/Idempotence).

The Bucket Snake policies should not be modified outside of Bucket Snake. You can modify any policy outside
of the Bucket Snake managed ones -- Bucket Snake will not alter or modify them. This is useful should you need to add additional permissions than what Bucket Snake would provide.

## Which permissions are created?
See the next section for details.
