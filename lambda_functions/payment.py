import json
import boto3
import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
history_table = dynamodb.Table('UserPosterHistory')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event)) # Debug log

    # FIX: Handle both stringified body (Proxy/Mapping) and direct dict (Test console)
    raw_body = event.get("body", "{}")
    
    if isinstance(raw_body, str):
        try:
            body = json.loads(raw_body)
        except:
            body = {}
    elif isinstance(raw_body, dict):
        body = raw_body
    else:
        body = {}

    user_id = body.get("user_id", "")
    prompt_used = body.get("prompt_used", "")

    if not user_id or not prompt_used:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "User ID and prompt are required."})
        }

    try:
        # Query for the specific poster using user_id and prompt_used as an attribute filter
        response = history_table.scan(
            FilterExpression="user_id = :user_id and prompt_used = :prompt_used",
            ExpressionAttributeValues={
                ":user_id": user_id,
                ":prompt_used": prompt_used
            }
        )

        # Check if the poster exists
        if "Items" not in response or not response["Items"]:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Poster not found for this user with the given prompt."})
            }

        # Update the payment status for the specific poster
        poster = response["Items"][0]  # Getting the first match

        # Update the 'paid' status of the matched poster
        update_response = history_table.update_item(
            Key={
                'user_id': user_id,
                'timestamp': poster['timestamp']  # Use the timestamp from the found item
            },
            UpdateExpression="SET paid = :paid",
            ExpressionAttributeValues={
                ":paid": True
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Payment marked successful for the specific poster."})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to mark payment: {str(e)}"})
        }
