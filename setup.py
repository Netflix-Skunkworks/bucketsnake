"""
Bucket Snake
==========
AWS Lambda function that grantsss S3 permissionsss at ssscale.
"""
import sys
import os.path

from setuptools import setup, find_packages

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src/ directory to the sys.path.
sys.path.insert(0, ROOT)

about = {}
with open(os.path.join(ROOT, "bucket_snake", "__about__.py")) as f:
    exec(f.read(), about)

install_requires = [
    "boto3",
    "swag-client",
    "retrying>=1.3.3",
    "raven_python_lambda"
]

tests_require = [
    'pytest',
    'moto',
    'coveralls',
]

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__email__"],
    url=about["__uri__"],
    description=about["__summary__"],
    long_description='See README.md',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'tests': tests_require
    },
    entry_points={},
    keywords=['aws', 'account_management', "s3", "security", "iam", "lambda", "sss", "snake"]
)
