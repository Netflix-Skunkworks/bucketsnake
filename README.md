Bucket Snake
=======================
[![serverless](http://public.serverless.com/badges/v3.svg)](http://www.serverless.com) [![Build Status](https://travis-ci.org/Netflix-Skunkworks/bucketsnake.svg?branch=master)](https://travis-ci.org/Netflix-Skunkworks/bucketsnake) [![Coverage Status](https://coveralls.io/repos/github/Netflix-Skunkworks/bucketsnake/badge.svg)](https://coveralls.io/github/Netflix-Skunkworks/bucketsnake)

## This project is in heavy development and not yet ready for production use

<p align="center"><img src="website/static/img/logo.png" alt="logo" width="30%" height="30%" /></p>

Bucket Snake is an AWS Lambda function that provisions S3 access for IAM roles. A primary feature
of Bucket Snake is to create IAM roles that reside in the account where the S3 buckets live to facilitate
proper cross-account S3 bucket access (via a role assumption).

Documentation
-------------
Bucket Snake's documentation [can be found here](https://Netflix-Skunkworks.github.io/bucketsnake).
