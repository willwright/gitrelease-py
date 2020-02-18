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

    path_dict = event["pathParameters"]
    projectslug = path_dict["projectslug"]
    print("projectslug: {}".format(projectslug))

    try:
        response = table.query(
            IndexName="projectslug-index",
            KeyConditionExpression=Key('projectslug').eq(projectslug)
        )
    except ClientError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": e.response['Error']['Message']
            }),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(response),
    }


def version_get_handler(event, context):
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

    path_dict = event["pathParameters"]
    projectslug = path_dict["projectslug"]
    version = path_dict["version"]

    try:
        response = table.get_item(Key={
            'projectslug': projectslug,
            'version': version
        })
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
                "body": json.dumps(response['Item'])
            }

    return {
        "statusCode": 200,
        "body": ""
    }


def version_candidate_get_handler(event, context):
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

    path_dict = event["pathParameters"]
    projectslug = path_dict["projectslug"]
    version = path_dict["version"]
    candidate = path_dict["candidate"]

    try:
        response = table.get_item(Key={
            'projectslug#version#candidate': '{}#{}#{}'.format(projectslug, version, candidate)
        })
    except ClientError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": e.response['Error']['Message']
            }),
        }

    return {
        "statusCode": 200,
        "headers": {},
        "isBase64Encoded": False,
        "body": json.dumps(response)
    }
