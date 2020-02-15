from ast import literal_eval
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import decimal
import json


def post_handler(event, context):
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
    release_dict = event["body"]

    # When input comes from API Gateway event["body"] is a string so we need to cast it to dictionary
    if not isinstance(release_dict, dict):
        release_dict = literal_eval(release_dict)

    try:
        response = table.put_item(Item=release_dict)
    except ClientError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": e.response['Error']['Message']
            }),
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "item": "",
        }),
    }
