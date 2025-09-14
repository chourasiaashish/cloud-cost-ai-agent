
import logging
from typing import Dict, Any
from http import HTTPStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for processing Bedrock agent requests.
    
    Args:
        event (Dict[str, Any]): The Lambda event containing action details
        context (Any): The Lambda context object
    
    Returns:
        Dict[str, Any]: Response containing the action execution results
    
    Raises:
        KeyError: If required fields are missing from the event
    """
    def get_named_parameter(event, name):
        """
        Get a parameter from the lambda event
        """
        return next(item for item in event['parameters'] if item['name'] == name)['value']

    try:
        action_group = event['actionGroup']
        function = event['function']
        message_version = event.get('messageVersion',1)
        parameters = event.get('parameters', [])


        # Execute your business logic here. For more information, 
        # refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
        if function == 'get_ec2_cost':
            # Example: Call AWS Pricing API to get EC2 cost details
            import boto3
            import json
            pricing_client = boto3.client('pricing', region_name='us-east-1')
            #instanceType = get_named_parameter(event, "instanceType")
            vcpu = get_named_parameter(event, "vcpu")
            memory = get_named_parameter(event, "memory")
            memory=memory + " GiB"
            operatingSystem = get_named_parameter(event, "operatingSystem")
            
            response = pricing_client.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    #{"Type": "TERM_MATCH", "Field": "instanceType", "Value": "m5.large"},
                    {"Type": "TERM_MATCH", "Field": "vcpu", "Value": vcpu},
                    {"Type": "TERM_MATCH", "Field": "memory", "Value": memory},
                    {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": operatingSystem},
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                    {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                    {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'}
                ],
                MaxResults=1
            )
            # Parse the pricing JSON
            price_item = json.loads(response["PriceList"][0])
            sku = list(price_item["terms"]["OnDemand"].keys())[0]

            instanceType=price_item["product"]["attributes"]["instanceType"]
            price_dimensions = price_item["terms"]["OnDemand"][sku]["priceDimensions"]
            price_per_unit = price_dimensions[list(price_dimensions.keys())[0]]["pricePerUnit"]["USD"]
            print(f"On-Demand price for ${instanceType} Linux in US East (N. Virginia): ${price_per_unit}/hour")
            response_body = {
                'TEXT': {
                    'body': f'EC2 Cost Details: {price_per_unit} USD/hour for {instanceType} in N. Virginia'
                }
            }
        else:
            response_body = {
                'TEXT': {
                    'body': f'The function {function} is not implemented yet.'
                }
            }
        action_response = {
            'actionGroup': action_group,
            'function': function,
            'functionResponse': {
                'responseBody': response_body
            }
        }
        response = {
            'response': action_response,
            'messageVersion': message_version
        }

        logger.info('Response: %s', response)
        return response

    except KeyError as e:
        logger.error('Missing required field: %s', str(e))
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'body': f'Error: {str(e)}'
        }
    except Exception as e:
        logger.error('Unexpected error: %s', str(e))
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': 'Internal server error'
        }