import json
import boto3
import base64
import datetime

# Clients
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")

BUCKET_NAME = "movie-poster-design-caa900"
TABLE_NAME = "UserPosterHistory"
MAX_PROMPT_LEN = 512  # Titan v2 hard limit

def save_history(user_id, prompt, poster_url):
    """Stores poster info in DynamoDB."""
    timestamp = datetime.datetime.utcnow().isoformat()

    dynamodb.put_item(
        TableName=TABLE_NAME,
        Item={
            "user_id": {"S": user_id},
            "timestamp": {"S": timestamp},
            "prompt_used": {"S": prompt},
            "paid": {"BOOL": False},
            "poster_url": {"S": poster_url}
        }
    )

def lambda_handler(event, context):
    print("Received event:", json.dumps(event)) # Debug log

    prompt = event.get("prompt")
    user_id = event.get("user_id")

    if not prompt:
        qs = event.get("queryStringParameters")
        if qs:
            prompt = qs.get("prompt")
            user_id = qs.get("user_id")

    # 3. If not found, try body (Proxy Integration POST)
    if not prompt:
        body = event.get("body")
        if body:
            try:
                if isinstance(body, str):
                    body = json.loads(body)
                if isinstance(body, dict):
                    prompt = body.get("prompt")
                    user_id = body.get("user_id")
            except:
                pass
    
    # Default user_id if missing
    if not user_id:
        user_id = "anonymous_user"

    if not prompt:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Prompt is required. Event received: " + str(event)})
        }

    # Titan v2 max limit = 512 characters
    prompt = prompt[:MAX_PROMPT_LEN]

    # Build Titan v2 request body
    body = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 1024,
            "width": 1024,
            "cfgScale": 8
        }
    }

    try:
        # Call Bedrock Titan v2
        response = bedrock.invoke_model(
            modelId="amazon.titan-image-generator-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )

        # Parse image
        result = json.loads(response["body"].read())
        image_b64 = result["images"][0]
        image_bytes = base64.b64decode(image_b64)

        # Create file name
        filename = f"poster-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.png"

        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=image_bytes,
            ContentType="image/png",
            ACL='public-read'
        )

        # Construct permanent public URL
        # Note: Bucket must have public read access or object ACL must be public-read
        presigned_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

        # Save record in DynamoDB
        save_history(user_id, prompt, presigned_url)

        # Return the URL
        return {
            "statusCode": 200,
            "body": json.dumps({"poster_url": presigned_url})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
