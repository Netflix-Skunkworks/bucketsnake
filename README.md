Bucket Snake
=======================
[![serverless](http://public.serverless.com/badges/v3.svg)](http://www.serverless.com) [![Build Status](https://travis-ci.org/Netflix-Skunkworks/bucketsnake.svg?branch=master)](https://travis-ci.org/Netflix-Skunkworks/bucketsnake) [![Coverage Status](https://coveralls.io/repos/github/Netflix-Skunkworks/bucketsnake/badge.svg)](https://coveralls.io/github/Netflix-Skunkworks/bucketsnake)

## This project is in heavy development and not yet ready for production use

<p align="center"><img src="docs/images/logo.png" alt="logo" width="30%" height="30%" /></p>

Bucket Snake is an AWS Lambda function that provisions S3 access for IAM roles. A primary feature
of Bucket Snake is to crete IAM roles that reside in the account where the S3 buckets live to facilitate 
proper cross-account S3 bucket access (via a role assumption).

General Summary
---------------
S3 access in a large AWS deployment with many accounts can be challenging. This is complicated by the S3 permissions model
of object and bucket ownership. [See AWS S3 documentation for additional details](http://docs.aws.amazon.com/AmazonS3/latest/dev/access-policy-alternatives-guidelines.html).

Bucket Snake utilizes a permissions pattern that relies on IAM roles as [documented here](http://docs.aws.amazon.com/AmazonS3/latest/dev/example-walkthroughs-managing-access-example4.html).

### S3 Permissions Complexity
Common S3 challenges to that one will often encounter:
1. Which account owns an S3 bucket? (AWS S3 ARNs lack account IDs.)
1. Which specific S3 permissions are actually required for performing the actions I need?
1. What about cross-account access? What's the best way of granting permissions for cross-account without
   having to rely on ACLs on each and every object?

Bucket Snake resolves the above by:
1. Relying on Historical's S3 Report JSON (Full look-up table of all S3 buckets you own, and which account they reside in)
1. Abstracting S3 permissions into simple `list`, `get`, `put`, and `delete` actions against a bucket and prefix.
1. IAM role provisioning in destination bucket accounts with correct `sts:AssumeRole` and S3 permissions grant the required
   permissions and avoid bucket-and-object ownership issues.

### Cross-account access issues?
Cross-account S3 access can create a number of headaches and hard-to-scale infrastructures if the S3 bucket and
corresponding objects are owned by different accounts. Please review [the documentation](http://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-auth-workflow-object-operation.html)
on how AWS authorizes S3 access object access.

**TL;DR:** You always want to use an IAM role within the bucket-owning account for placing (as well as reading)
objects to avoid bucket-and object ownership mismatches. Otherwise, the account that owns the objects will need
to explicitly add an ACL to each and every object that requires additional accounts to access. This massively
increases S3 permissions complexity.

Because Bucket Snake relies on IAM to grant permissions, object-ACLs are no longer required, thus eliminating
cross-account ownership issues.

Dependencies
-----------------
Bucket Snake depends on [Historical](https://github.com/Netflix-Skunkworks/historical), and the [Historical S3 Report](https://github.com/Netflix-Skunkworks/historical-reports).


How to Install
----------------------
Bucket Snake can be deployed with [Serverless](https://serverless.com).  See the serverless examples in the `docs` directory.

### Configuration
Bucket Snake has a number of environment variables that it can be configured with:

|      Environment Variable     	|          Default Value          	| Required 	|                                                                                                         Environment-Variable Description                                                                                                         	|                                                                  Example                                              |
|:-----------------------------:	|:-------------------------------:	|:--------:	|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:	|:----------------------------------------------------------------------------------------------------------------------------------------:	|
| `APP_REPORTS_BUCKETS`         	| None                            	| YES      	| This is a comma-separated list of S3 bucket names which contain the historical S3 report JSON. This is a list to permit applications to use per-region buckets.                                                             	| `"historical-report-bucket-us-east-1,historical-report-bucket-us-west-2,historical-report-bucket-eu-west-1"` (Replace with your buckets) 	|
| `SWAG_BUCKET`                 	| None                            	| YES      	| This is the S3 bucket that contains the [SWAG](https://github.com/Netflix-Skunkworks/https://github.com/Netflix-Skunkworks/swag-api) data set.                                                                              	| `swag-data-set-bucket-here`                                                                                                              	|
| `SWAG_REGION`                 	| None                            	| YES      	| The region for where the SWAG bucket  lives.                                                                                                                                                                                	| `us-east-1` (Replace with your SWAG bucket region)                                                                                       	|
| `SWAG_DATA_FILE`              	| None                            	| YES      	| The prefix to where the accounts JSON lives in the SWAG bucket.                                                                                                                                                             	| `v2/accounts.json`  (Replace with your prefix)                                                                                           	|
| `REPORTS_BUCKET`              	| None                            	| YES      	| The S3 bucket that contains the Historical S3 report JSON that Bucket  Snake will use. This is just 1 bucket vs. a list for what is granted to the application.                                                             	| `"historical-report-bucket-us-east-1"` (Replace with your bucket)                                                                        	|
| `REPORTS_REGION`              	| None                            	| YES      	| The region of the S3 bucket that contains the historical report.                                                                                                                                                            	| `us-east-1` (Replace with your Historical report bucket region)                                                                          	|
| `REPORTS_PREFIX`              	| `historical-s3-report.json`     	| No       	| The prefix for the S3 report JSON.  This prefix needs to point to a historical report that only has the bucket region and account ID. See the Historical-Reports examples on generating a "lite" version  of the S3 report. 	| See Default                                                                                                                              	|
| `BLACKLISTED_SOURCE_ACCOUNTS` 	| None                            	| No       	| A comma-separated list of AWS 12-digit account IDs for where source IAM roles are not permitted to use Bucket Snake for S3 access. Bucket Snake will not operate for source application IAM roles in these accounts.        	| `"0123456678910,012345678911"` (Replace with your account IDs)                                                                           	|
| `BLACKLISTED_BUCKET_ACCOUNTS` 	| None                            	| No       	| A comma-separated list of AWS 12-digit account IDs for accounts that Bucket Snake should not grant S3 access. I.e. a bucket in an account that is protected, and Bucket Snake should not be granting access to.             	| `"0123456678910,012345678911"` (Replace with your account IDs)                                                                           	|
| `BUCKET_SNAKE_POLICY_NAME`    	| `BucketSnake`                   	| No       	| The IAM policy name on the IAM role that grants S3 access.                                                                                                                                                                  	| See Default                                                                                                                              	|
| `STS_POLICY_NAME`             	| `BucketSnakeAssumeRole`         	| No       	| The IAM policy name on the source IAM role that grants `sts:AssumeRole` permissions to the destination AWS account S3 roles.                                                                                                	| See Default                                                                                                                              	|
| `DEST_ROLE_DESCRIPTION`       	| `Bucket Snake provisioned role` 	| No       	| The description to the destination S3 IAM roles provisioned by Bucket Snake.                                                                                                                                                	| See Default                                                                                                                              	|
| `BUCKET_SNAKE_ROLE`           	| `BucketSnake`                   	| No       	| The name of the IAM role that Bucket Snake needs to assume into to perform destination AWS account activities.                                                                                                              	| See Default                                                                                                                              	|
| `BUCKET_SNAKE_SESSION_NAME`   	| `BucketSnake`                    	| No       	| The name of the STS session name that Bucket Snake will use when it assumes to the destination AWS account IAM roles.                                                                                                       	| See Default                                                                                                                              	|
| `IAM_REGION`                  	| `us-east-1`                     	| No       	| The AWS region for where IAM API commands are sent.                                                                                                                                                                         	| See Default                                                                                                                              	|


How to Trigger
---------------
Bucket Snake is triggered from a lambda invocation with a payload that looks like so:

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

## What does this do exactly?
Bucket Snake would receive the JSON from the lambda invocation, and from that, would:
1. Verify that the source IAM exists
1. Verify that the buckets exist, and are not exempted buckets (more on this in the configuration section)
1. Determine which S3 buckets are in the same account as the source application, and which are not
1. For buckets in the same account, Bucket Snake will add in the proper S3 permissions to the source app IAM role
1. For buckets that are not in the same account, Bucket Snake will create IAM roles in the destination accounts
   with access to the respective buckets (IAM role name is: `AppName-12DigitSourceAccountNumber`). This role will
   have a trust policy that allows the source application `sts:AssumeRole` access to it.
1. If applicable, a policy will be added to the source IAM role to grant `sts:AssumeRole` access to those destination
   IAM roles
1. And lastly, Bucket Snake will grant access to the Historical S3 report's JSON file so that application knows 
   which S3 buckets require the role assumption for access.

## How does my application make use of this?
At present no "Bucket Snake aware" client library exists. We are currently in the process of developing one for Python
and Java.

This client would work by fetching the Historical S3 JSON (access granted by Bucket Snake), and then from there,
before the client would perform the S3 operation, it would check if the S3 bucket is in the same account (this information
lives in the Historical report). If it's in the same account, then the client directly access the bucket with the on-instance
IAM credentials. If it's in a different account, the client would first assume to the destination role (named `AppName-12DigitSourceAccountNumber`),
cache the credentials for future use (re-assume when expired), and then use those assumed credentials to access the S3 bucket.
