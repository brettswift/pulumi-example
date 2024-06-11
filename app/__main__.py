import pulumi
import pulumi_aws as aws
from pulumi_aws import s3, sqs
from sqs_lambda_events import EventsQueueToLambda, EventsQueueToLambdaArgs
import simple_lambda as simple_lambda

account_id = aws.get_caller_identity().account_id
stack = pulumi.get_stack()
project = pulumi.get_project()
project_stack = f"{project}-{stack}"
# Reference to the data stack, and import resources
data_stack_ref = pulumi.StackReference(
    f"organization/pulumi-coffee-data/{pulumi.get_stack()}"
)
bucket_name = data_stack_ref.get_output("bucket_name")
output_bucket: s3.Bucket = s3.Bucket.get(
    "data_bucket", id=bucket_name, bucket=bucket_name
)

# pulumi.log.info(f"Bucket Name: {output_bucket.bucket}")
output_bucket.bucket.apply(lambda bucket: pulumi.log.info(f"Bucket Name: {bucket}"))

queue = sqs.Queue("ingress_queue", name=f"{project_stack}_ingress-queue")
handler_args = simple_lambda.SimpleLambdaArgs(
    codepath="../lambdas/queue_processor/",
    description="Handles Queue Events",
    env_vars={
        "BUCKET_NAME": output_bucket.bucket,
        "PREFIX_PATH": f"{project_stack}",
    },
)

queue_consumer_lambda = simple_lambda.SimpleLambda(
    "queue-events-handler",
    handler_args,
   
)

events_queue_to_lambda_args = EventsQueueToLambdaArgs(
    lambda_function_name=queue_consumer_lambda.lambda_function.name,
    lambda_role_name=queue_consumer_lambda.lambda_role.name,
    queue=queue,
)
EventsQueueToLambda("queue_events", events_queue_to_lambda_args, opts=pulumi.ResourceOptions(depends_on=queue_consumer_lambda))

# Create an S3 bucket access policy
bucket_policy = aws.iam.RolePolicy(
    "bucket-policy",
    role=queue_consumer_lambda.lambda_role.name,
    policy=pulumi.Output.all(output_bucket.arn).apply(
        lambda args: f"""{{
    "Version": "2012-10-17",
    "Statement": [
        {{
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:ListObjects",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "{args[0]}/*"
        }}
    ]
}}"""
    ),
)

# Export outputs
pulumi.export("queue_url", queue.id)
pulumi.export("bucket_name", output_bucket.id)
pulumi.export("bucket_prefix", f"{project_stack}")
pulumi.export(
    "log_group_name",
    pulumi.Output.concat("/aws/lambda/", queue_consumer_lambda.lambda_function.name),
)

pulumi.export("lambda-role-name", queue_consumer_lambda.lambda_role.name)

# commands to facilitate the demo
pulumi.export(
    "command_push_to_queue",
    "aws sqs send-message --queue-url $(pulumi stack output queue_url) --message-body 'Hello, Cayliens!'",
)

pulumi.export(
    "command_queue_contents",
    "aws sqs get-queue-attributes --queue-url $(pulumi stack output queue_url) --attribute-names ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible",
)
pulumi.export(
    "command_view_s3",
    "aws s3 ls  s3://$(pulumi stack output bucket_name)/$(pulumi stack output bucket_prefix)/",
)
