---
id: s3background
title: S3 Background Information
sidebar_label: S3 Background
---

AWS S3 has a complex permissions model. Before continuing, please review the following documents:

- [S3 Access Control Overview](http://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-overview.html)
- [How Amazon S3 Authorizes a Request](http://docs.aws.amazon.com/AmazonS3/latest/dev/how-s3-evaluates-access-control.html)
- [How Amazon S3 Authorizes a Request for a Bucket Operation](http://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-auth-workflow-bucket-operation.html)
- **And Perhaps Most Importantly: [How Amazon S3 Authorizes a Request for an Object Operation](http://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-auth-workflow-object-operation.html)**

## Bucket Owner and Object Owner?

S3 has a complex permissions model that examines the "owner" of a resource when making an access decision.

An "Owner" refers to an AWS account which the resource belongs to. With regards to a bucket, this is the account that a bucket "resides" in.

So, if account `Foo` had a bucket named `thebucket`, `Foo` would be the owner of `thebucket`.

Objects also have ownership. Object ownership refers to the AWS account that _put_ the object into the bucket.

So, if an IAM role in account `Foo` put an object into the `thebucket` bucket, then the object would be owned by `Foo`.

### Cross-account ownership

When bucket and object ownership is the same (that is the account that owns the bucket and the object are the same), then access is straightforward. In this case, IAM in the account, as well as the bucket policy determines whether or not access is granted to the object.

Trouble begins when the ownership is different. Buckets can hold objects that belong to different AWS accounts. For example: Take two AWS accounts: `Foo` and `Bar`. Bucket `thebucket` resides in account `Foo`. `Bar` has an IAM role named `theRole` that can place an object named `theobj` in `thebucket`. If an application with `theRole` (`Bar` account) places the object, the object will reside in `thebucket` (owned by `Foo`), but the object will be owned by `Bar`.

This may not seem like an issue at first, however, reviewing [AWS's documentation regarding object access](http://docs.aws.amazon.com/AmazonS3/latest/dev/access-control-auth-workflow-object-operation.html), access to this object will ultimately be determined by the `Bar` account. That is achieved when `Bar` places an ACL on `theobj` to explicitly grant another AWS account access.

In this example, without any ACLs applied to `theobj`, despite `Foo` being the owner of the `thebucket` bucket, IAM roles in `Foo` won't be able to read the object or otherwise manipulate it. `Foo` will be able to see that the object is there, and can delete the object, but can't otherwise make any modifications to it.

To resolve this issue, `Bar` would need to add an ACL to `theobj` so that `Foo` has access to it. One common way to resolve this is to put the `bucket-owner-full-control` canned ACL on the object. While that may alleviate access issues in this example, it does not fully resolve the issue.

### ACLs are a bad solution
The `bucket-owner-full-control` canned ACL may seem like a solution to this problem, but it's not. The owner of the object in this example is still not the same as the owner of the bucket. Thus, the decision to read/write/modify the object is still determined by `Bar` (the object owning account).

If a new account, `Baz` requires access to the bucket and objects within it, the ACL of the objects would need to be altered again to permit `Baz` access. This is where scalability becomes very difficult over time. This complexity gets significantly worse as objects and accounts increase.

### IAM Roles can permanently solve this problem
Avoiding cross-account object and bucket ownership is *strongly* advised. This is resolved by always performing S3 operations with an IAM role within the bucket owning account. Doing this ensures that the bucket owner and object owner are the same.

This also helps simplify access by reducing the number of places where S3 permissions can live, which ultimately improves the security of your infrastructure.
