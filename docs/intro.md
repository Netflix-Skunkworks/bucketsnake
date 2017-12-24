---
id: intro
title: Introduction
sidebar_label: Introduction
---

**This project is in heavy development and not yet ready for production use!**

Bucket Snake is an AWS Lambda function that provisions S3 access for IAM roles. A primary feature
of Bucket Snake is to create IAM roles that reside in the account where the S3 buckets live. This facilitates
proper cross-account S3 bucket access (via IAM role assumption).

S3's permission model complicates S3 access in large environments. This complexity is increased with
S3's use of Bucket and Object ownership. When the ownership of buckets and objects are different,
there can be annoying and hard to scale permissions issues.  By using IAM roles in the same account
a bucket lives in, you can avoid mis-matched ownership and rely on IAM and/or S3 bucket policies
to permit access to buckets. Avoiding ACLs makes S3 access much easier to manage at scale.

## Bucket-Snake aware S3 clients?
Bucket Snake provisions the IAM roles for access. But, this is only 1/2 of the solution. The second
half is to have an S3 client that is aware of:
1. The location of the S3 buckets
1. The role to assume into

With the above, an application should be able to access any bucket required in your infrastructure without
ever needing to worry about per-object permissions.

**Currently, there are no Bucket-Snake aware ready-to-use clients. This is under active development!**

## S3 Permissions Complexity
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
**TL;DR:** You always want to use an IAM role within the bucket-owning account for placing (as well as reading)
objects to avoid bucket-and object ownership mismatches. Otherwise, the account that owns the objects will need
to explicitly add an ACL to each and every object that requires additional accounts to access. This massively
increases S3 permissions complexity.

The next section documents this in detail.
