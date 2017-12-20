"""
.. module: bucket_snake.tests.conf
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
SWAG_BUCKET = "swagbucket"
HISTORICAL_REPORT_BUCKET = "historical-reports"

EXISTING_ASPD = {
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "sts:AssumeRole"
        }
    ]
}
