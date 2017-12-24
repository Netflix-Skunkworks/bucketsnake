---
id: installation
title: Deploying the Bucket Snake Lambda Function
sidebar_label: Deployment
---

Bucket Snake can be deployed with [Serverless](https://serverless.com). See the [docs/serverless-examples](https://github.com/Netflix-Skunkworks/bucketsnake/tree/master/docs/serverless-examples) for an example.

## What is required?
Bucket Snake depends on [SWAG](https://github.com/Netflix-Skunkworks/swag-api), [Historical](https://github.com/Netflix-Skunkworks/historical), and the [Historical S3 Report](https://github.com/Netflix-Skunkworks/historical-reports).

For a summary of these tools, please visit their respective pages and review the documentation.

### Historical S3 Report
Bucket Snake has a hard dependency on the Historical S3 Report, which is provided as part of the [Historical-Reports](https://github.com/Netflix-Skunkworks/historical-reports).

Bucket Snake doesn't require much from the report. It requires:
1. The bucket name
1. The bucket region
1. The bucket account

This can be achieved with a Historical S3 report that has the `EXCLUDE_FIELDS` environmental variable configured with the value:

    Name,_version,Grants,LifecycleRules,Logging,Policy,Tags,Versioning,Website,Cors,Notifications,Acceleration,Replication,CreationDate,AnalyticsConfigurations,MetricsConfigurations,InventoryConfigurations

A slim report is not required -- but it makes for a smaller JSON file for client applications to fetch from S3 (or have included with their deployment).

#### Historical Report Bucket
An S3 Bucket that contains this report must be available for the Bucket Snake lambda function. This is required to be set in the configuration. (See the next section for details)

The Historical S3 report should live in a bucket that all applications in your infrastructure can access. This will allow applications to fetch this file to make a determination if cross-account access is required.

### SWAG
SWAG is a hard requirement for Bucket Snake. The JSON must be accessible in S3 and is configurable. (See the next section for details)

## IAM Roles
Bucket Snake operates from a hub-spoke type of model. The lambda function itself requires an IAM role, which then assumes into other account IAM roles to provision the S3 access for a given application.

Please use your favorite tool to sync these roles out across your environment.

#### Bucket Snake Lambda Function IAM Role

The trust policy must be similar to:

    {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                }
            }
        ]
    }

The inline-polices must be similar to:

    {
        "Statement": [
            {
                "Sid": "Logs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            },
            {
                "Sid": "HistoricalS3",
                "Effect": "Allow",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::historical-s3-report-bucket/prefix/to/historical-s3-reports.json"
            },
            {
                "Sid": "AssumeToRoles",
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": "arn:aws:iam::*:role/BucketSnake"
            }
        ]
    }


#### In-account Bucket Snake IAM Role (Destination Roles)

The trust policy must be similar to:

    {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Principal": {
                    "AWS": "arn:aws:iam::SOURCE-BUCKET-SNAKE-LAMBDA-ACCOUNT-HERE:role/BucketSnakeLambdaProfile"
                }
            }
        ]
    }

The inline-polices must be similar to:

    {
        "Statement": [
            {
                "Action": [
                    "iam:CreateRole",
                    "iam:GetRole",
                    "iam:PutRolePolicy",
                    "iam:UpdateAssumeRolePolicy"
                ],
                "Resource": "*",
                "Effect": "Allow"
            }
        ]
    }
