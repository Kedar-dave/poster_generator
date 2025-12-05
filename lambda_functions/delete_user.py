import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("UserLoginData")

def lambda_handler(event, context):
    user_id = event.get("queryStringParameters", {}).get("user_id")

    if not user_id:
        return {"statusCode": 400, "body": json.dumps({"error": "user_id required"})}

    table.delete_item(Key={"user_id": user_id})

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "User deleted successfully"})
    }
