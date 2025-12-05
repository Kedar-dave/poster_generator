import json
import boto3
import logging
from boto3.dynamodb.conditions import Key

# Set up DynamoDB resource
dynamodb = boto3.resource("dynamodb")
history_table = dynamodb.Table("UserPosterHistory")
user_table = dynamodb.Table("UserLoginData")

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    # Extract user_id from event
    user_id = event.get("user_id", "")

    # 1. Validate user_id
    if not user_id:
        logger.error("No user_id provided in the request.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "User ID is required."})
        }

    try:
        # -------------------------------------------------------------
        # 2. CHECK IF USER EXISTS IN UserLoginData
        # -------------------------------------------------------------
        user_check = user_table.get_item(
            Key={"user_id": user_id}
        )

        if "Item" not in user_check:
            logger.warning(f"Unauthorized attempt: user {user_id} not found.")
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "User does not exist. Access denied."})
            }

        # -------------------------------------------------------------
        # 3. Fetch poster history
        # -------------------------------------------------------------
        resp = history_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )

        if "Items" not in resp or not resp["Items"]:
            logger.info(f"No posters found for user {user_id}.")
            return {
                "statusCode": 200,
                "body": json.dumps([])
            }

        posters = []
        for poster in resp["Items"]:

            # Paid poster → show URL
            if poster.get("paid", False):
                poster["locked"] = False
                poster["poster_url"] = poster.get("poster_url", "")

            # Unpaid poster → locked
            else:
                poster["locked"] = True
                poster["poster_url"] = None

            posters.append(poster)

        logger.info(f"Found {len(posters)} posters for user {user_id}.")
        return {
            "statusCode": 200,
            "body": json.dumps(posters)
        }

    except Exception as e:
        logger.error(f"Error while processing request for {user_id}: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error. Please try again later."})
        }
