import aws_cdk as core
import aws_cdk.assertions as assertions

from week1_cdk.week1_cdk_stack import Week1CdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in week1_cdk/week1_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = Week1CdkStack(app, "week1-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
