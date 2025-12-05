import json
import boto3
import hashlib

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("UserLoginData")

def lambda_handler(event, context):

    raw_body = event.get("body", {})

    # Accept both dict and string bodies
    if isinstance(raw_body, dict):
        body = raw_body
    else:
        try:
            body = json.loads(raw_body)
        except:
            body = {}

    user_id = body.get("user_id")
    password = body.get("password")

    if not user_id or not password:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "user_id and password are required"})
        }

    # CHANGE THIS LINE
    table.put_item(
        Item={"user_id": user_id, "password": password}
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "User created"})
    }