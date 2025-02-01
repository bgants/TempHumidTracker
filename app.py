#!/usr/bin/env python3
import os

import aws_cdk as cdk

from temp_humid_tracker.temp_humid_tracker_stack import TempHumidTrackerStack

account = os.getenv("AWS_ACCOUNT_ID")
primary_region = os.getenv("AWS_PRIMARY_REGION")
domain_name = os.getenv("AWS_DOMAIN_NAME")
primary_environment = cdk.Environment(account=account, region=primary_region)

app = cdk.App()
TempHumidTrackerStack(app, "TempHumidTrackerStack", env=primary_environment, domain_name=domain_name)
app.synth()
