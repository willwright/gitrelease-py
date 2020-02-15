import json

import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def get_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table('Releases')

    pathDict = event["pathParameters"]
    projectslug = pathDict["projectslug"]

    try:
        response = table.get_item(Key={'projectslug': projectslug})
    except ClientError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": e.response['Error']['Message']
            }),
        }
    else:
        if 'Item' in response:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "item": response['Item'],
                }),
            }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "item": "",
        }),
    }
