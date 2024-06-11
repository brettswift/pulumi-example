import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource, Output


class EventsQueueToLambdaArgs:
    """
    Arguments for the QueueLambdaLinker component.
    """

    def __init__(
        self,
        lambda_function_name: Output[str],
        lambda_role_name: Output[str],
        queue: aws.sqs.Queue,
    ):
        self.lambda_function_name = lambda_function_name
        self.lambda_role_name = lambda_role_name
        self.queue = queue


class EventsQueueToLambda(ComponentResource):
    """
    A component to link AWS SQS queue events to a Lambda function.
    """

    def __init__(self, name: str, args: EventsQueueToLambdaArgs, opts=None):
        super().__init__("custom:queuelambda_events", name, None, opts)
        self.name = name
        self.args = args
        self.create_resources()

    def create_resources(self) -> None:
        self.create_policy_and_attach()
        self.event_source_mapping = self.create_event_source_mapping()

    def create_event_source_mapping(self) -> aws.lambda_.EventSourceMapping:
        return aws.lambda_.EventSourceMapping(
            f"{self.name}-sqs-event-mapping",
            event_source_arn=self.args.queue.arn,
            batch_size=1,
            function_name=self.args.lambda_function_name,
            opts=pulumi.ResourceOptions(depends_on=[self.args.queue]),
        )

    def create_policy_and_attach(self) -> None:
        # Create a policy that allows the 'sqs:ReceiveMessage' action
        policy = aws.iam.Policy(
            f"{self.name}-sqs-policy",
            description=f"Policy for {self.name} lambda function",
            policy=pulumi.Output.all(self.args.queue.arn).apply(
                lambda args: {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": [
                                "sqs:ReceiveMessage",
                                "sqs:DeleteMessage",
                                "sqs:GetQueueAttributes",
                                "lambda:CreateEventSourceMapping",
                                "lambda:ListEventSourceMappings",
                                "lambda:InvokeFunction",
                            ],
                            "Effect": "Allow",
                            "Resource": args[0],
                        }
                    ],
                }
            ),
        )

        # Attach the policy to the lambda function role
        aws.iam.RolePolicyAttachment(
            f"{self.name}-sqs-policy-attachment",
            role=self.args.lambda_role_name,
            policy_arn=policy.arn,
        )
