"""
.. module: bucket_snake.util.exceptions
    :platform: Unix
    :copyright: (c) 2017 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. author:: Mike Grima <mgrima@netflix.com>
"""


class BucketSnakeException(Exception):
    pass


class InvalidRequestException(BucketSnakeException):
    pass


class SourceRoleDoesNotExistException(BucketSnakeException):
    pass


class BlacklistedAccountException(BucketSnakeException):
    pass


class S3BucketDoesNotExistException(BucketSnakeException):
    pass


class MissingRequiredConfigurationItemException(BucketSnakeException):
    pass
