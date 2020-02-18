import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json


def issue_post_handler(event, context):
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

    event_dict = event["body"]
    projectslug = event_dict["fields__project__key"]
    version = event_dict["fields__fixVersions"][0]["name"]
    print(version)

    try:
        response = table.scan(
            FilterExpression=Attr("projectslug").eq(projectslug) & Attr("version").eq(version)
        )
    except ClientError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": e.response['Error']['Message']
            })
        }

    items_list = sorted(response["Items"], key=lambda x: int(x["candidate"]))

    # Load the release with the highest candidate increment
    realease_dict = items_list[len(items_list)-1]

    # Add/Remove branch form the release
    realease_dict["branches"].append()

    try:
        response = table.update_item(
            Key={
                "projectslug#version#candidate": "{}#{}#{}".format(last_candidate_dict["projectslug"], last_candidate_dict["version"], last_candidate_dict["candidate"])
            },
            UpdateExpression="set int."
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
        "body": json.dumps()
    }