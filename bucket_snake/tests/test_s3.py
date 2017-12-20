"""
.. module: bucket_snake.tests.test_s3
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""
from bucket_snake.s3.permissions import (
    check_if_cross_account,
    build_bucket_account_mapping,
    create_access_to_reports,
    collect_policies,
    create_s3_role_policies,
    S3_PERMISSIONS
)


def test_check_if_cross_account(bucket_table):
    assert not check_if_cross_account("012345678910", "test-bucket-one")
    assert check_if_cross_account("012345678910", "test-bucket-three")


def test_build_bucket_account_mapping(config, bucket_table, s3_role_event):
    buckets_same, buckets_cross = build_bucket_account_mapping(s3_role_event)

    assert len(buckets_same) == 2
    assert len(buckets_cross) == 2

    # With a bucket that doesn't exist:
    s3_role_event["buckets"]["imaginary_bucket"] = [
        {
            "prefix": "*",
            "perms": [
                "list"
            ]
        }
    ]
    # TODO: Don't forget to test for buckets that don't exist and buckets that are blacklisted


def test_collect_policies(buckets_same_account_mapping):
    collected_policies = collect_policies(buckets_same_account_mapping)

    list_arns = [
        "arn:aws:s3:::test-bucket-one",
        "arn:aws:s3:::test-bucket-two"
    ]

    get_arns = [
        "arn:aws:s3:::test-bucket-one/some/path/*",
        "arn:aws:s3:::test-bucket-two/*"
    ]

    put_delete_arn = "arn:aws:s3:::test-bucket-one/some/path/*"

    assert len(collected_policies["012345678910"]) == 4

    assert len(collected_policies["012345678910"]["list"]) == len(list_arns)
    for list_arn in list_arns:
        assert list_arn in collected_policies["012345678910"]["list"]

    assert len(collected_policies["012345678910"]["get"]) == len(get_arns)
    for get_arn in get_arns:
        assert get_arn in collected_policies["012345678910"]["get"]

    assert len(collected_policies["012345678910"]["put"]) == 1
    assert collected_policies["012345678910"]["put"].pop() == put_delete_arn

    assert len(collected_policies["012345678910"]["delete"]) == 1
    assert collected_policies["012345678910"]["delete"].pop() == put_delete_arn


def test_create_s3_role_policies(buckets_same_account_mapping):
    role_policies = create_s3_role_policies(collect_policies(buckets_same_account_mapping))

    test_arns = {
        "list": [
            "arn:aws:s3:::test-bucket-one",
            "arn:aws:s3:::test-bucket-two"
        ],
        "get": [
            "arn:aws:s3:::test-bucket-one/some/path/*",
            "arn:aws:s3:::test-bucket-two/*"
        ],
        "put": ["arn:aws:s3:::test-bucket-one/some/path/*"],
        "delete": ["arn:aws:s3:::test-bucket-one/some/path/*"]
    }

    assert len(role_policies) == 1
    assert len(role_policies["012345678910"]["Statement"]) == 4

    for s in role_policies["012345678910"]["Statement"]:
        # Verify that the Sid is correct:
        perm = s["Sid"].lower()
        assert test_arns.get(perm)

        # Verify all the correct S3 permissions are present for the given policy
        assert len(s["Action"]) == len(S3_PERMISSIONS[perm])
        for p in S3_PERMISSIONS[perm]:
            assert p in s["Action"]

        # Verify all the ARNs are present:
        assert len(s["Resource"]) == len(test_arns[perm])
        for a in test_arns[perm]:
            assert a in s["Resource"]


def test_create_access_to_reports(buckets_same_account_mapping, config):
    # With existing mapping:
    role_policies = create_s3_role_policies(collect_policies(buckets_same_account_mapping))
    assert len(role_policies["012345678910"]["Statement"]) == 4
    create_access_to_reports(role_policies, "012345678910")
    assert len(role_policies["012345678910"]["Statement"]) == 5

    assert role_policies["012345678910"]["Statement"][4]["Sid"] == "HistoricalS3Reports"
    assert role_policies["012345678910"]["Statement"][4]["Effect"] == "Allow"
    assert role_policies["012345678910"]["Statement"][4]["Action"] == "s3:GetObject"
    assert role_policies["012345678910"]["Statement"][4]["Resource"] == \
        ["arn:aws:s3:::historical-reports/historical-s3-report.json"]

    # And without:
    role_policies = {}
    create_access_to_reports(role_policies, "012345678910")
    assert len(role_policies["012345678910"]["Statement"]) == 1
    assert role_policies["012345678910"]["Statement"][0]["Sid"] == "HistoricalS3Reports"
    assert role_policies["012345678910"]["Statement"][0]["Effect"] == "Allow"
    assert role_policies["012345678910"]["Statement"][0]["Action"] == "s3:GetObject"
    assert role_policies["012345678910"]["Statement"][0]["Resource"] == \
        ["arn:aws:s3:::historical-reports/historical-s3-report.json"]
