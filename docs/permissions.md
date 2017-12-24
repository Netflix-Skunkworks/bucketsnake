---
id: permissions
title: Bucket Snake S3 Permissions
sidebar_label: Permission Reference
---

Bucket Snake abstracts S3 permissions into the following categories:

1. `list`
1. `get`
1. `put`
1. `delete`

## Bucket vs. Object level permissions
S3 has two types of S3 permissions:
1. Bucket permissions
1. Object permissions

Bucket permissions are applied to an entire bucket, whereas object permissions are applied to a prefix within a bucket.

_List_ permissions are _bucket-level_ permissions ([more info here](http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html#using-with-s3-actions-related-to-buckets)). Granting `list` access to a bucket will grant access to list the contents of an entire S3 bucket. When Bucket Snake generates the IAM permissions, it will always make `list` a separate statement. Thus, lumping `list` permissions with other object-level permissions is fine; Bucket Snake will handle this properly.

Object-level permissions will be applied to the specified prefix that is provided. Object-level permissions are [defined here](http://docs.aws.amazon.com/AmazonS3/latest/dev/using-with-s3-actions.html#using-with-s3-actions-related-to-objects).

## S3 -> IAM Permissions Mapping
The abstracted S3 permissions are transformed into the following IAM permissions:
1. `list`
    - `s3:ListBucket`
    - `s3:ListBucketVersions`
1. `get`
    - `s3:GetObject`
    - `s3:GetObjectTagging`
    - `s3:GetObjectVersion`
    - `s3:GetObjectVersionTagging`
    - `s3:GetObjectAcl`
    - `s3:GetObjectVersionAcl`
1. `put`
    - `s3:PutObject`
    - `s3:PutObjectTagging`
    - `s3:PutObjectVersionTagging`
    - `s3:ListMultipartUploadParts`*
    - `s3:AbortMultipartUpload`
    - `s3:RestoreObject`
1. `delete`
    - `s3:DeleteObject`
    - `s3:DeleteObjectTagging`
    - `s3:DeleteObjectVersion`
    - `s3:DeleteObjectVersionTagging`

_*Listing multipart uploads is typically used when performing multipart uploads, and as such, has been lumped in with `put` permissions._

## Sample Generated IAM Policy
The role provisioned in the bucket-residing account would look similar to this:

    {
        "Statement": [
            {
                "Sid": "List",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:ListBucketVersions"
                ],
                "Resource": [
                    "arn:aws:s3:::<bucket-name>",
                    # ... All the buckets that need listing here ...
                ]
            },
            {
                "Sid": "Get",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:GetObjectTagging",
                    "s3:GetObjectVersion",
                    "s3:GetObjectVersionTagging"
                ],
                "Resource": [
                    "arn:aws:s3:::<bucket-name>/<prefix>",
                    # ... All the buckets and prefixes requiring get access here ...
                ]
            },
            {
                "Sid": "Put",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:PutObjectTagging",
                    "s3:PutObjectVersionTagging",
                    "s3:ListMultipartUploadParts",
                    "s3:AbortMultipartUpload",
                    "s3:RestoreObject"
                ],
                "Resource": [
                    "arn:aws:s3:::<bucket-name>/<prefix>",
                    # ... All the buckets and prefixes requiring put access here ...
                ]
            },
            {
                "Sid": "Delete",
                "Effect": "Allow",
                "Action": [
                    "s3:DeleteObject",
                    "s3:DeleteObjectTagging",
                    "s3:DeleteObjectVersion",
                    "s3:DeleteObjectVersionTagging"
                     ],
                "Resource": [
                    "arn:aws:s3:::<bucket-name>/<prefix>",
                    # ... All the buckets and prefixes requiring delete access here ...
                ]
            }
        ]
    }

The source application would be given an inline policy to assume to the destination IAM role, which looks like:

    {
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "sts:AssumeRole",
                "Resource": [
                    "arn:aws:iam::<dest-role-account-number>:role/<app-name>-<12-digit-app-account-number>",
                    # ... All the roles to assume into here ...
                ]
            }
        ]
    }

## Limitations
IAM has a [limitation](http://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-limits.html) of 64 characters for IAM role names. The format that is chosen for destination account with the format declared for cross-account roles is `<AppName>-<12-digit-AppAccountNumber>`, this leaves 51 characters remaining for application names. Thus, applications with names that are more than 51 characters are not supported by Bucket Snake.
