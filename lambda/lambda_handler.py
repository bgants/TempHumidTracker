from decimal import Decimal
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

import boto3
import os
import json


dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

logger = Logger()

@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    logger.info(event)
    body = json.loads(event['body'])
    location = body['location']
    sensor_datetime = body['sensor_datetime']
    temperature = body['temperature']
    humidity = body['humidity']
    
    try:
        if not location or not temperature or not humidity:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid request')
            }
        temperature = Decimal(str(temperature))
        humidity = Decimal(str(humidity))    
        table.put_item(
            Item={
                'sensor_id': context.aws_request_id,
                'location': location,
                'sensor_datetime': sensor_datetime,
                'temperature': temperature,
                'humidity': humidity
            }
        )    
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
    
