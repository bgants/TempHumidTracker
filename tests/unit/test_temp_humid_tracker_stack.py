import aws_cdk as core
import aws_cdk.assertions as assertions

from temp_humid_tracker.temp_humid_tracker_stack import TempHumidTrackerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in temp_humid_tracker/temp_humid_tracker_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TempHumidTrackerStack(app, "temp-humid-tracker")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
