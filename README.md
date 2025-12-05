# Movie Poster Generator

A Flask-based web application that uses Generative AI (Amazon Bedrock) to create custom movie posters based on user prompts.

## Project Overview

This application allows users to:
1.  **Sign Up/Login**: Secure user authentication.
2.  **Generate Posters**: Enter a prompt to generate a unique movie poster using AI.
3.  **View History**: See a history of generated posters.
4.  **Unlock Posters**: "Pay" (simulate payment) to unlock and view the full-resolution poster URL.

### Architecture High-Level
-   **Frontend**: Flask (Python) Web App.
-   **Backend**: AWS Serverless (API Gateway, Lambda).
-   **Database**: Amazon DynamoDB.
-   **Storage**: Amazon S3.
-   **AI Model**: Amazon Bedrock (Titan Image Generator v2).

## Prerequisites

-   Python 3.8+
-   `pip` (Python package manager)
-   AWS Credentials (if deploying or running backend locally, though the app currently points to deployed APIs).

## Installation & Setup

1.  **Clone the repository** (if not already done).
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Ensure `flask`, `requests`, `python-dotenv`, and `boto3` are in `requirements.txt`.*

3.  **Environment Configuration**:
    Create a `.env` file in the root directory if it doesn't exist. It should contain the API endpoints:
    ```env
    USER_API_URL=https://bgwp6whvle.execute-api.us-east-1.amazonaws.com/dev/user
    POSTER_API_BASE=https://kiqi41dlld.execute-api.us-east-1.amazonaws.com/dev
    ```

## Running the Application

1.  **Start the Flask Server**:
    ```bash
    python app.py
    ```
2.  **Access the App**:
    Open your browser and navigate to `http://127.0.0.1:5000`.

## Usage Walkthrough

1.  **Home Page**: You will see the landing page. Click "Login" or "Sign Up".
2.  **Sign Up**: Create a new account with an email and password.
3.  **Login**: Log in with your credentials.
4.  **Dashboard**:
    -   **Generate**: Enter a text prompt (e.g., "A sci-fi movie about a robot detective") and click "Generate".
    -   **History**: You will see your generated poster in the list. Initially, it might be "Locked".
    -   **Unlock**: Click the "Pay/Unlock" button to simulate payment. The page will reload, and the poster image will be revealed.

## Project Structure

-   `app.py`: Main Flask application handling routes and API calls.
-   `lambda_functions/`: Contains the Python code for AWS Lambda functions.
-   `templates/`: HTML templates for the web interface.
-   `static/`: Static assets (CSS, JS, images).
