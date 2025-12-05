import json
import boto3
import hashlib

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("UserLoginData")


def parse_body(event):
    """Handles cases where event['body'] is dict or JSON string."""
    body = event.get("body", {})

    # Case 1: body is already a dict
    if isinstance(body, dict):
        return body

    # Case 2: body is a JSON string
    if isinstance(body, str) and body.strip() != "":
        try:
            return json.loads(body)
        except:
            pass

    # Fallback: empty dict
    return {}


def lambda_handler(event, context):
    body = parse_body(event)

    user_id = body.get("user_id")
    new_password = body.get("password")

    if not user_id or not new_password:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "user_id and new password required"})
        }

    # Hash the new password
    hashed_pw = hashlib.sha256(new_password.encode()).hexdigest()

    # Update password in DynamoDB
    table.update_item(
        Key={"user_id": user_id},
        UpdateExpression="SET password = :p",
        ExpressionAttributeValues={":p": hashed_pw}
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Password updated successfully"})
    }
