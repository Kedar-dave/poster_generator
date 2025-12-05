import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("UserLoginData")

def lambda_handler(event, context):
    user_id = event.get("queryStringParameters", {}).get("user_id")

    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "user_id required"})}

    resp = table.get_item(Key={"user_id": user_id})

    if "Item" not in resp:
        return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}

    # FIX: Return password hash so the frontend/backend can verify it
    return {
        "statusCode": 200,
        "body": json.dumps({
            "user_id": resp["Item"]["user_id"],
            "password": resp["Item"]["password"]
        })
    }
