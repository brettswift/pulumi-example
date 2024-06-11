import json

import pulumi
import pulumi_aws as aws
from pulumi import ComponentResource

class SimpleLambdaArgs:
    """
    Mirrors arguments from aws.lambda.FunctionArgs.
    """
    def __init__(
        self,
        codepath: str,
        timeout: int = 15,
        handler: str = "handler.handler",
        memory_size: int = 640,
        description: str = "",
        env_vars: dict = {},
    ):
        self.codepath = codepath
        self.handler = handler
        self.memory_size = memory_size
        self.timeout = timeout
        self.description = description
        self.env_vars = env_vars


class SimpleLambda(ComponentResource):
    """
    An adapter to simplify aws.lambda.Function
    """
    # public resources
    lambda_function = aws.lambda_.Function
    lambda_role = aws.iam.Role

    def __init__(self, name: str, args: SimpleLambdaArgs, opts=None):
        super().__init__(
            "caylent:commons:lambda:simple_lambda", name, {}, opts
        )
        self.name = name.replace("_", "-").lower()
        self.region = aws.get_region().name
        self.stack = pulumi.get_stack()
        self.project = pulumi.get_project()
        self.project_stack = f"{self.project}-{self.stack}" 
        self.long_name = f"{self.project_stack}-{self.name}"
        self.args = args
        self.child_opts = pulumi.ResourceOptions(parent=self)
        self.create_resources()

    def create_resources(self) -> None:
        self.lambda_role = self.create_lambda_role()
        self.lambda_function = self.create_lambda(self.lambda_role)

    def create_lambda_role(
        self,
    ) -> aws.iam.Role:
        role = aws.iam.Role(
            f"{self.name}-lambda",
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Principal": {"Service": "lambda.amazonaws.com"},
                            "Effect": "Allow",
                            "Sid": "",
                        }
                    ],
                }
            ),
            opts=self.child_opts,
        )

        aws.iam.RolePolicyAttachment(
            f"{self.name}-BasicExecutionRole",
            role=role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
        )

        # for name, policy_arn in policy_arns.items():
        #     aws.iam.RolePolicyAttachment(
        #         name,
        #         role=role.name,
        #         policy_arn=policy_arn,
        #         opts=self.child_opts,
        #     )

        return role

    # def create_lambda_s3_policy(self) -> aws.iam.policy:
    #     return aws.iam.Policy(
    #         f"{self.name}-lambda-bucket-access",
    #         description="policy to access S3 bucket",
    #         policy=self.args.s3_bucket.apply(
    #             lambda arn: json.dumps(
    #                 {
    #                     "Version": "2012-10-17",
    #                     "Statement": [
    #                         {
    #                             "Effect": "Allow",
    #                             "Action": [
    #                                 "s3:*",
    #                             ],
    #                             "Resource": f"{arn}/*",
    #                         }
    #                     ],
    #                 }
    #             )
    #         ),
    #         opts=self.child_opts,
    #     )

    def create_lambda(
        self,
        role: aws.iam.Role,
    ) -> aws.lambda_.Function:

        codepath = self.args.codepath
        handler = self.args.handler

        exporter = aws.lambda_.Function(
            f"{self.long_name}-function",
            description=self.args.description,
            code=pulumi.FileArchive(codepath),
            handler=handler,
            memory_size=self.args.memory_size,
            role=role.arn,
            runtime="python3.8",
            timeout=self.args.timeout,
            environment=aws.lambda_.FunctionEnvironmentArgs(
                variables=self.args.env_vars
            ),
            opts=self.child_opts,
        )

        return exporter

