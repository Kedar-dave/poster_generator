# API Documentation

This document details the API endpoints used by the Movie Poster Generator application.

## Base URLs
-   **User API**: `https://bgwp6whvle.execute-api.us-east-1.amazonaws.com/dev`
-   **Poster API**: `https://kiqi41dlld.execute-api.us-east-1.amazonaws.com/dev`

---

## User Management

### 1. Create User
Creates a new user account.

-   **Endpoint**: `/user`
-   **Method**: `POST`
-   **URL**: `[User API Base]/user`
-   **Body** (JSON):
    ```json
    {
      "user_id": "user@example.com",
      "password": "hashed_password"
    }
    ```
-   **Response** (200 OK):
    ```json
    {
      "message": "User created"
    }
    ```

### 2. Get User (Login)
Retrieves user details for authentication.

-   **Endpoint**: `/user`
-   **Method**: `GET`
-   **URL**: `[User API Base]/user`
-   **Query Parameters**:
    -   `user_id`: Email of the user.
-   **Response** (200 OK):
    ```json
    {
      "user_id": "user@example.com",
      "password": "hashed_password"
    }
    ```

---

## Poster Operations

### 3. Generate Poster
Generates a movie poster based on a prompt.

-   **Endpoint**: `/movie-poster-api-design`
-   **Method**: `GET`
-   **URL**: `[Poster API Base]/movie-poster-api-design`
-   **Query Parameters**:
    -   `user_id`: Email of the user.
    -   `prompt`: Description of the poster to generate.
-   **Response** (200 OK):
    ```json
    {
      "poster_url": "https://s3-bucket-url/poster.png"
    }
    ```

### 4. Get History
Retrieves the list of generated posters for a user.

-   **Endpoint**: `/history`
-   **Method**: `GET`
-   **URL**: `[Poster API Base]/history`
-   **Query Parameters**:
    -   `user_id`: Email of the user.
-   **Response** (200 OK):
    ```json
    [
      {
        "user_id": "user@example.com",
        "timestamp": "2023-10-27T10:00:00",
        "prompt_used": "A sci-fi movie...",
        "paid": false,
        "locked": true,
        "poster_url": null
      },
      {
        "user_id": "user@example.com",
        "timestamp": "2023-10-26T10:00:00",
        "prompt_used": "A western movie...",
        "paid": true,
        "locked": false,
        "poster_url": "https://..."
      }
    ]
    ```

### 5. Unlock Poster (Pay)
Marks a poster as paid/unlocked.

-   **Endpoint**: `/pay`
-   **Method**: `POST`
-   **URL**: `[Poster API Base]/pay`
-   **Body** (JSON):
    ```json
    {
      "user_id": "user@example.com",
      "prompt_used": "A sci-fi movie..."
    }
    ```
-   **Response** (200 OK):
    ```json
    {
      "message": "Payment marked successful for the specific poster."
    }
    ```
