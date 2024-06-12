import pulumi
import pulumi_aws as aws
from pulumi_aws import s3

account_id = aws.get_caller_identity().account_id
stack = pulumi.get_stack()
project = pulumi.get_project()
project_stack = f"{project}-{stack}"

bucket_name = f"{project_stack}-{account_id}"
bucket = s3.Bucket(bucket_name, bucket=bucket_name, force_destroy=True)

pulumi.export("bucket_name", bucket.bucket)
