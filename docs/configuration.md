---
id: configuration
title: Configuring the Bucket Snake Lambda Function
sidebar_label: Configuration
---

Bucket Snake has a number of environment variables that it can be configured with.  The table below outlines what they are and if they are required.

<table>
    <col width="190px" />
    <col width="120px" />
    <thead>
        <tr>
            <th class="centerCell">Environment Variable</th>
            <th class="centerCell">Default Value</th>
            <th class="centerCell">Required</th>
            <th class="centerCell">Environment-Variable Description</th>
            <th class="centerCell">Example</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td class="centerCell"><code>APP_REPORTS_BUCKETS</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell"><strong>YES</strong></td>
            <td class="nocenterCell">This is a comma-separated list of S3 bucket names which contain the historical S3 report JSON. This is a list to permit applications to use per-region buckets.</td>
            <td class="centerCell"><code>"historical-report-bucket-us-east-1,historical-report-bucket-us-west-2,historical-report-bucket-eu-west-1"</code><br />(Replace with your buckets)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>SWAG_BUCKET</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell"><strong>YES</strong></td>
            <td class="nocenterCell">This is the S3 bucket that contains the <a href="https://github.com/Netflix-Skunkworks/swag-api">SWAG</a> data set.</td>
            <td class="centerCell"><code>"swag-data-set-bucket-here"</code><br />(Replace with your bucket)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>SWAG_REGION</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell"><strong>YES</strong></td>
            <td class="nocenterCell">The region for where the SWAG bucket lives.</td>
            <td class="centerCell"><code>"us-east-1"</code><br />(Replace with your SWAG bucket region)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>SWAG_DATA_FILE</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell"><strong>YES</strong></td>
            <td class="nocenterCell">The prefix to where the accounts JSON lives in the SWAG bucket.</td>
            <td class="centerCell"><code>"v2/accounts.json"</code><br />(Replace with your prefix)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>REPORTS_BUCKET</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell"><strong>YES</strong></td>
            <td class="nocenterCell">The S3 bucket that contains the Historical S3 report JSON that Bucket Snake will use. This is just 1 bucket vs. a list for what is granted to the application.</td>
            <td class="centerCell"><code>"historical-report-bucket-us-east-1"</code><br />(Replace with your bucket)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>REPORTS_REGION</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell"><strong>YES</strong></td>
            <td class="nocenterCell">The region of the S3 bucket that contains the historical report.</td>
            <td class="centerCell"><code>"us-east-1"</code><br />(Replace with your Historical report bucket region)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>REPORTS_PREFIX</code></td>
            <td class="centerCell"><code>"historical-s3-report.json"</code></td>
            <td class="centerCell"><strong>No</strong></td>
            <td class="nocenterCell">The region of the S3 bucket that contains the historical report.</td>
            <td class="centerCell">See Default</td>
        </tr>
        <tr>
            <td class="centerCell"><code>BLACKLISTED_SOURCE_ACCOUNTS</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">A comma-separated list of AWS 12-digit account IDs for where source IAM roles are not permitted to use Bucket Snake for S3 access. Bucket Snake will not operate for source application IAM roles in these accounts.</td>
            <td class="centerCell"><code>"0123456678910,012345678911"</code><br />(Replace with your account IDs)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>BLACKLISTED_BUCKET_ACCOUNTS</code></td>
            <td class="centerCell">None</td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">A comma-separated list of AWS 12-digit account IDs for accounts that Bucket Snake should not grant S3 access. I.e. a bucket in an account that is protected, and Bucket Snake should not be granting access to.</td>
            <td class="centerCell"><code>"0123456678910,012345678911"</code><br />(Replace with your account IDs)</td>
        </tr>
        <tr>
            <td class="centerCell"><code>BUCKET_SNAKE_POLICY_NAME</code></td>
            <td class="centerCell"><code>"BucketSnake"</code></td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">The IAM policy name on the IAM role that grants S3 access.</td>
            <td class="centerCell">See Default</td>
        </tr>
        <tr>
            <td class="centerCell"><code>STS_POLICY_NAME</code></td>
            <td class="centerCell"><code>"BucketSnakeAssumeRole"</code></td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">The IAM policy name on the source IAM role that grants <code>sts:AssumeRole</code> permissions to the destination AWS account S3 roles.</td>
            <td class="centerCell">See Default</td>
        </tr>
        <tr>
            <td class="centerCell"><code>DEST_ROLE_DESCRIPTION</code></td>
            <td class="centerCell"><code>"Bucket Snake provisioned role"</code></td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">The description to the destination S3 IAM roles provisioned by Bucket Snake.</td>
            <td class="centerCell">See Default</td>
        </tr>
        <tr>
            <td class="centerCell"><code>BUCKET_SNAKE_ROLE</code></td>
            <td class="centerCell"><code>"BucketSnake"</code></td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">The name of the IAM role that Bucket Snake needs to assume into to perform destination AWS account activities.</td>
            <td class="centerCell">See Default</td>
        </tr>
        <tr>
            <td class="centerCell"><code>BUCKET_SNAKE_SESSION_NAME</code></td>
            <td class="centerCell"><code>"BucketSnake"</code></td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">The name of the STS session name that Bucket Snake will use when it assumes to the destination AWS account IAM roles.</td>
            <td class="centerCell">See Default</td>
        </tr>
        <tr>
            <td class="centerCell"><code>IAM_REGION</code></td>
            <td class="centerCell"><code>"us-east-1"</code></td>
            <td class="centerCell">No</td>
            <td class="nocenterCell">The AWS region for where IAM API commands are sent.</td>
            <td class="centerCell">See Default</td>
        </tr>
    </tbody>
</table>

These variables can be supplied in the [serverless](https://github.com/Netflix-Skunkworks/bucketsnake/tree/master/docs/serverless-examples) configuration.
