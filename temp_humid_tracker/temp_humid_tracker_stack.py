from aws_cdk import (
    Stack,    
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    aws_dynamodb as dynamodb
)
import aws_cdk as cdk
from constructs import Construct

from lambda_layer.python.aws_lambda_powertools.event_handler import api_gateway

class TempHumidTrackerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, domain_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        domain_name = domain_name
        
        # DynamoDB Table
        table = dynamodb.Table(
            self, "TemperatureHumidityTable",
            partition_key={"name": "location", "type": dynamodb.AttributeType.STRING},
            sort_key={"name": "sensor_id", "type": dynamodb.AttributeType.STRING},
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        
        # Defina a Lambda Layer
        lambda_layer = _lambda.LayerVersion(
            self, "TempHumidTrackerLayer",
            code=_lambda.Code.from_asset("lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="A layer for TempHumidTracker Lambda functions"
        )
        
        # Create a Lambda function
        Lambda_function = _lambda.Function(
            self, "TempHumidTrackerFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("lambda"),
            layers=[lambda_layer],
            environment={                
                "POWERTOOLS_SERVICE_NAME": "TempHumidTracker",
                "POWER_TOOLS_LOG_LEVEL": "INFO",
                "TABLE_NAME": table.table_name
            }
        )

        # Grant Lambda permissions to write to the DynamoDB table
        table.grant_read_write_data(Lambda_function)
                
        # Create an API Gateway
        api = apigateway.RestApi(self, "TempHumidTrackerApi")
        
        # Creat a resource
        job_resource = api.root.add_resource("jobs")
        
        # Add POST method to the resource
        job_resource.add_method(
            "POST", apigateway.LambdaIntegration(Lambda_function))
        
        # Create a Hosted Zone
        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone", domain_name=domain_name)
        
        # Creat a Certificate
        certificate = acm.Certificate(
            self, "Certificate",
            domain_name=domain_name,
            validation=acm.CertificateValidation.from_dns(hosted_zone))
        
        # Create a Custom Domain Name
        domain = apigateway.DomainName(
            self, "CustomDomainName",
            domain_name=domain_name,
            certificate=certificate,
            endpoint_type=apigateway.EndpointType.REGIONAL
        )
        
        # Add base path mapping to the API
        domain.add_base_path_mapping(api,
                base_path="v1",
                stage=api.deployment_stage)
        
        # Add ARecord to the Hosted Zone
        route53.ARecord(
            self, "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.ApiGatewayDomain(domain)
            ),
        )
   
