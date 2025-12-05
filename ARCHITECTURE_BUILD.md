# Architecture Build Guide

This guide provides step-by-step instructions to recreate the AWS backend architecture for the Movie Poster Generator.

## Prerequisites
-   AWS Account
-   AWS CLI installed and configured (optional, but recommended)
-   Python 3.8+ installed

---

## Step 1: DynamoDB Tables

Create two DynamoDB tables.

### Table 1: UserLoginData
-   **Table Name**: `UserLoginData`
-   **Partition Key**: `user_id` (String)
-   **Sort Key**: None
-   **Capacity**: On-Demand or Provisioned (Free Tier eligible)

### Table 2: UserPosterHistory
-   **Table Name**: `UserPosterHistory`
-   **Partition Key**: `user_id` (String)
-   **Sort Key**: `timestamp` (String)
-   **Capacity**: On-Demand or Provisioned

---

## Step 2: S3 Bucket

Create an S3 bucket to store the generated images.

-   **Bucket Name**: `movie-poster-design-caa900` (or a unique name of your choice)
-   **Region**: `us-east-1` (Recommended for Bedrock availability)
-   **Permissions**:
    -   Uncheck "Block all public access" (if you want to serve images directly via public URLs).
    -   **Bucket Policy**: Add a policy to allow `GetObject` if you want public read access.
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::movie-poster-design-caa900/*"
            }
        ]
    }
    ```

---

## Step 3: IAM Roles

Create an IAM Role for your Lambda functions.

-   **Role Name**: `MoviePosterLambdaRole`
-   **Permissions Policies**:
    -   `AmazonDynamoDBFullAccess` (or scoped down to specific tables)
    -   `AmazonS3FullAccess` (or scoped down to specific bucket)
    -   `AmazonBedrockFullAccess` (Required for image generation)
    -   `AWSLambdaBasicExecutionRole` (for CloudWatch logging)

---

## Step 4: Lambda Functions

Create the following Lambda functions using Python 3.x. Assign the `MoviePosterLambdaRole` to all of them.

### 1. Create User
-   **Function Name**: `CreateUser`
-   **Code**: Copy content from `lambda_functions/create_user.py`

### 2. Get User
-   **Function Name**: `GetUser`
-   **Code**: Copy content from `lambda_functions/get_user.py`

### 3. Poster Designer (Generator)
-   **Function Name**: `PosterDesigner`
-   **Code**: Copy content from `lambda_functions/poster_designer.py`
-   **Configuration**:
    -   **Timeout**: Increase to 1-2 minutes (Image generation can take time).
    -   **Environment Variables**:
        -   `BUCKET_NAME`: `movie-poster-design-caa900`
        -   `TABLE_NAME`: `UserPosterHistory`

### 4. Payment
-   **Function Name**: `PaymentUpdate`
-   **Code**: Copy content from `lambda_functions/payment.py`

### 5. Get History
-   **Function Name**: `GetHistory`
-   **Code**: Copy content from `lambda_functions/get_history.py`

---

## Step 5: API Gateway

Create REST APIs to expose the Lambda functions.

### API 1: User API
-   **Name**: `UserAPI`
-   **Resource**: `/user`
-   **Methods**:
    -   `POST` -> Integration: Lambda Function (`CreateUser`)
    -   `GET` -> Integration: Lambda Function (`GetUser`)
-   **Deploy**: Create a Stage (e.g., `dev`). Note the Invoke URL.

### API 2: Poster API
-   **Name**: `PosterAPI`
-   **Resource**: `/movie-poster-api-design`
    -   `GET` -> Integration: Lambda Function (`PosterDesigner`)
-   **Resource**: `/pay`
    -   `POST` -> Integration: Lambda Function (`PaymentUpdate`)
-   **Resource**: `/history`
    -   `GET` -> Integration: Lambda Function (`GetHistory`)
-   **Deploy**: Create a Stage (e.g., `dev`). Note the Invoke URL.

---

## Step 6: Connect Frontend

1.  Update the `.env` file in your Flask project with the Invoke URLs from Step 5.
    -   `USER_API_URL`: `[User API Invoke URL]/user`
    -   `POSTER_API_BASE`: `[Poster API Invoke URL]`

2.  Run the Flask app and test the flow!
