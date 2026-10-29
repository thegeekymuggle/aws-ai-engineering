# from aws_cdk import (
#     # Duration,
#     Stack,
#     # aws_sqs as sqs,
# )
# from constructs import Construct

# class Week1CdkStack(Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # The code that defines your stack goes here

#         # example resource
#         # queue = sqs.Queue(
#         #     self, "Week1CdkQueue",
#         #     visibility_timeout=Duration.seconds(300),
#         # )



from aws_cdk import (
    Stack, Duration, RemovalPolicy, CfnOutput,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
)
from constructs import Construct


class Week1CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Storage ---
        bucket = s3.Bucket(
            self, "DataBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,                       # deny any non-HTTPS request
            removal_policy=RemovalPolicy.DESTROY,   # practice project: delete on destroy
            auto_delete_objects=True,               # ...even if it has files in it
        )

        # Upload a test file as part of the deploy
        s3deploy.BucketDeployment(
            self, "SeedData",
            sources=[s3deploy.Source.data("hello.txt", "hello from cdk")],
            destination_bucket=bucket,
        )

        # --- Compute ---
        log_group = logs.LogGroup(
            self, "ReaderLogs",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        fn = lambda_.Function(
            self, "Reader",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="lambda_function.lambda_handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={"BUCKET": bucket.bucket_name},
            memory_size=256,
            timeout=Duration.seconds(10),
            log_group=log_group,
        )

        # --- Permissions: replaces your two JSON files + three IAM commands ---
        bucket.grant_read(fn)

        # --- API ---
        api = apigw.HttpApi(self, "Api")
        api.add_routes(
            path="/read",
            methods=[apigw.HttpMethod.GET],
            integration=integrations.HttpLambdaIntegration("ReadIntegration", fn),
        )

        # --- Print useful values after deploy ---
        CfnOutput(self, "ApiUrl", value=f"{api.url}read?key=hello.txt")
        CfnOutput(self, "BucketName", value=bucket.bucket_name)