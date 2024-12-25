# API Endpoint Table of Contents

| Category           | Endpoint                                                     | Method         | Description                                                  |
| ------------------ | ------------------------------------------------------------ | -------------- | ------------------------------------------------------------ |
| **Authentication** | [`/api/users/login/`](#login-api)                            | `POST`         | Authenticate user and obtain access and refresh tokens.      |
|                    | [`/api/users/logout/`](#logout-api)                          | `POST`         | Logout user by invalidating the refresh token.               |
|                    | [`/api/users/refresh-token/`](#token-refresh-api)            | `POST`         | Refresh the access token using a valid refresh token.        |
|                    | [`/api/users/signup/`](#signup-api-documentation)            | `POST`         | Register a new user account.                                 |
| **User Profiles**  | [`/api/users/profile/`](#userprofileview-api-documentation)  | `GET`, `PATCH` | Retrieve and update the current user's profile information.  |
|                    | [`/api/users/`](#userlistview-api-documentation)             | `GET`          | Retrieve a list of users (paginated, optional username filter). |
| **Friendships**    | [`/api/users/friendship/`](#friendship-api-documentation)    | `GET`          | Retrieve all friendship relationships for the current user.  |
|                    | [`/api/users/friendship/`](#friendship-api-documentation)    | `POST`         | Create a new friendship request.                             |
|                    | [`/api/users/friendship/`](#friendship-api-documentation)    | `PATCH`        | Update the status of an existing friendship.                 |
| **Messages**       | [`/api/messages/status/friendship/<uuid:friendship_id>/messages/`](#messagestatusview-api-documentation) | `GET`          | Retrieve paginated message statuses for a specific friendship. |

## Login API

### Description

The `Login API` endpoint allows users to authenticate by providing a valid username and password. Upon successful authentication, it returns a JSON Web Token (JWT) consisting of a **refresh token** and an **access token** for secure session management.

------

### Endpoint Details

- **Base Path:** `/api/users/`
- **Endpoint Path:** `/api/users/login/`
- **HTTP Method:** `POST`

------

### Request

#### Headers

- `Content-Type: application/json`

#### Body (JSON)

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

------

### Response

#### 1. Success (200 OK)

Returns the refresh and access tokens upon successful authentication:

```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

#### 2. Error (400 Bad Request)

Returned if the username or password is missing in the request:

```json
{
  "error": "Username and password are required"
}
```

#### 3. Error (401 Unauthorized)

Returned if the provided credentials are invalid:

```json
{
  "error": "Invalid Credentials"
}
```

------

### Logging

- **Success:** Logs a message indicating a successful login for the username.

- Failure:

   Logs a warning if:

  - Either `username` or `password` is missing.
  - The credentials are incorrect.

------

### Security Notes

- JWT tokens are generated using the `RefreshToken` class from `rest_framework_simplejwt`.
- Always use HTTPS to ensure secure communication between the client and the server.

------

### Examples

#### Successful Request

**Request:**

```http
POST /api/users/login/ HTTP/1.1
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

------

#### Invalid Request (Missing Password)

**Request:**

```http
POST /api/users/login/ HTTP/1.1
Content-Type: application/json

{
  "username": "john_doe"
}
```

**Response:**

```json
{
  "error": "Username and password are required"
}
```

------

#### Invalid Request (Incorrect Credentials)

**Request:**

```http
POST /api/users/login/ HTTP/1.1
Content-Type: application/json

{
  "username": "john_doe",
  "password": "wrong_password"
}
```

**Response:**

```json
{
  "error": "Invalid Credentials"
}
```



> [!NOTE]
>
> Usage Notes
>
> - The **access token** is used to authenticate API requests that require user authorization.
> - The **refresh token** is used to obtain a new access token when the current one expires.
> - Always store tokens securely on the client side.



## Logout API

### Description

The `Logout API` endpoint allows authenticated users to securely log out by blacklisting their **refresh token**. This ensures the token can no longer be used to generate new access tokens.

------

### Endpoint Details

- **Base Path:** `/api/users/`
- **Endpoint Path:** `/api/users/logout/`
- **HTTP Method:** `POST`
- **Authentication:** Required (Bearer Token)

------

### Request

#### Headers

- `Content-Type: application/json`
- `Authorization: Bearer <access_token>`

#### Body (JSON)

```json
{
  "refresh": "your_refresh_token"
}
```

------

### Response

#### 1. Success (200 OK)

Returns a success message when the user is logged out:

```json
{
  "message": "Successfully logged out"
}
```

#### 2. Error (400 Bad Request)

Returned if the **refresh token** is missing in the request:

```json
{
  "error": "Refresh token is required"
}
```

#### 3. Error (401 Unauthorized)

Returned if the provided **refresh token** is invalid or expired:

```json
{
  "error": "Invalid or expired refresh token"
}
```

#### 4. Error (401 Unauthorized)

Returned if there is a generic token-related error:

```json
{
  "error": "Invalid token"
}
```

------

### Logging

- **Success:** Logs a message indicating the user logged out successfully.

- Failure:

   Logs warnings or errors for:

  - Missing **refresh token**.
  - Invalid or expired **refresh token**.
  - Generic token-related errors.

------

> [!IMPORTANT]
>
> - **Blacklist Tokens:** This implementation uses the `django-rest-framework-simplejwt` blacklist feature to invalidate refresh tokens.
> - **Authorization Required:** Users must be authenticated to access this endpoint.

------

### Examples

#### Successful Logout

**Request:**

```http
POST /api/users/logout/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

**Response:**

```json
{
  "message": "Successfully logged out"
}
```

------

#### Missing Refresh Token

**Request:**

```http
POST /api/users/logout/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...

{
}
```

**Response:**

```json
{
  "error": "Refresh token is required"
}
```

------

#### Invalid or Expired Refresh Token

**Request:**

```http
POST /api/users/logout/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...

{
  "refresh": "invalid_or_expired_refresh_token"
}
```

**Response:**

```json
{
  "error": "Invalid or expired refresh token"
}
```

> [!NOTE]
>
> ## Usage Notes
>
> - Ensure the refresh token is included in the request body for the logout process.
> - Blacklisting the refresh token prevents it from being used to generate new access tokens, enhancing session security.
>
> 





## Token Refresh API

### Description

The `Token Refresh API` endpoint allows users to refresh their **access token** using a valid **refresh token**. If the refresh token is valid, the system either issues a new access token or rotates the refresh token based on the configuration.

------

### Endpoint Details

- **Base Path:** `/api/users/`
- **Endpoint Path:** `/api/users/refresh-token/`
- **HTTP Method:** `POST`
- **Authentication:** Required (Bearer Token)

------

### Request

#### Headers

- `Content-Type: application/json`
- `Authorization: Bearer <access_token>`

#### Body (JSON)

```json
{
  "refresh": "your_refresh_token"
}
```

------

### Response

#### 1. Success (200 OK)

Returns a new **access token** and possibly a new **refresh token** upon successful refresh:

```json
{
  "access": "new_access_token",
  "refresh": "new_refresh_token"  // Optional, based on settings
}
```

#### 2. Error (400 Bad Request)

Returned if the **refresh token** is missing in the request:

```json
{
  "error": "Refresh token is required"
}
```

#### 3. Error (401 Unauthorized)

Returned if the **refresh token** is invalid, expired, or missing the required `user_id`:

```json
{
  "error": "Invalid or expired refresh token"
}
```

#### 4. Error (401 Unauthorized)

Returned if there is a token-related error:

```json
{
  "error": "Invalid or expired refresh token"
}
```

------

### Logging

- **Success:** Logs a message indicating successful token refresh and whether the refresh token was blacklisted or rotated.

- Failure:

   Logs warnings or errors for:

  - Missing **refresh token**.
  - Invalid or expired **refresh token**.
  - Missing `user_id` in the refresh token.
  - Any generic token errors.

------

> [!TIP]
>
> ## Security Notes
>
> - **Rotation and Blacklisting:** If `ROTATE_REFRESH_TOKENS` is enabled, the **refresh token** is rotated and may be blacklisted based on the `BLACKLIST_AFTER_ROTATION` setting.
> - **Token Expiry:** The **access token** and **refresh token** expiration times are set based on the settings defined in `SIMPLE_JWT`.
> - **Authorization Required:** Users must be authenticated with a valid **access token** to use this endpoint.
>
> ------



### Examples

#### Successful Token Refresh

**Request:**

```http
POST /api/users/refresh-token/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...

{
  "refresh": "valid_refresh_token"
}
```

**Response:**

```json
{
  "access": "new_access_token",
  "refresh": "new_refresh_token"  // Only if rotation is enabled
}
```

------

#### Missing Refresh Token

**Request:**

```http
POST /api/users/refresh-token/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...

{
}
```

**Response:**

```json
{
  "error": "Refresh token is required"
}
```

------

#### Invalid or Expired Refresh Token

**Request:**

```http
POST /api/users/refresh-token/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...

{
  "refresh": "invalid_or_expired_refresh_token"
}
```

**Response:**

```json
{
  "error": "Invalid or expired refresh token"
}
```

> [!NOTE]
>
> ## Usage Notes
>
> - Refresh tokens are used to issue new **access tokens** without requiring users to log in again.
> - If the refresh token is valid and `ROTATE_REFRESH_TOKENS` is enabled, a new refresh token is issued, and the old one is blacklisted (if `BLACKLIST_AFTER_ROTATION` is enabled).
> - **Access tokens** are typically short-lived, while **refresh tokens** are used to obtain new access tokens after expiry.

------

## **SignUp API Documentation**

### **Endpoint:**

- **Base Path:** `/api/users/`
- **Endpoint Path:** `/api/users/signup/`
- **HTTP Method:** `POST`

### **Description:**

This endpoint allows users to register for the application. It accepts user details, including a username, email, password, and an optional profile image. The password undergoes validation to ensure it meets the security requirements. Upon successful registration, a refresh token and access token are returned for authentication.

### **Request Body:**

The request should be a `multipart/form-data` with the following fields:

```json
{
  "username": "string",        // (required) The username chosen by the user. It must be unique.
  "password": "string",        // (required) The password for the account. It must meet the validation criteria.
  "email": "string",           // (required) The user's email address. Must be a valid email format.
  "first_name": "string",      // (optional) The first name of the user.
  "last_name": "string",       // (optional) The last name of the user.
  "personal_image": "file"     // (optional) The user's profile image (image file in formats such as .jpg, .png).
}
```

### **Response:**

#### **Success (201 Created):**

```json
{
  "refresh": "string",    // (string) The refresh token used to generate a new access token.
  "access": "string"      // (string) The access token used to authenticate the user.
}
```

#### **Error (400 Bad Request):**

```json
{
  "error": "string"       // (string) Description of the error (e.g., missing required fields, invalid data).
}
```

#### **Error (401 Unauthorized):**

```json
{
  "error": "string"       // (string) Description of the error, typically related to authentication (e.g., invalid password).
}
```

### **Request Example:**

```http
POST /api/users/signup/ HTTP/1.1
Content-Type: multipart/form-data

{
  "username": "newuser",
  "password": "strongpassword123",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "personal_image": <image_file>
}
```

### **Response Example (Success):**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### **Response Example (Error):**

```json
{
  "error": "Password is too short. It must contain at least 8 characters."
}
```

### **Field Descriptions:**

- **`username`** (required): The unique username for the user account. It must be distinct from other usernames in the system.
- **`password`** (required): The password for the user account. It must comply with Django's password validation rules, ensuring strength and security.
- **`email`** (required): A valid email address associated with the user. It must follow proper email format.
- **`first_name`** (optional): The first name of the user. This field is optional and can be left blank.
- **`last_name`** (optional): The last name of the user. This field is optional and can be left blank.
- **`personal_image`** (optional): A profile image for the user. This field accepts image files (e.g., .jpg, .png) and is optional.

### **Password Validation:**

The password provided by the user will be validated according to the following criteria (as defined in the Django settings):

- **Minimum length of 8 characters.**
- **Must contain a mix of uppercase and lowercase letters, digits, and special characters.**

If the password does not meet these criteria, a `400 Bad Request` response will be returned with a specific error message explaining the failure.

### **Response Status Codes:**

- **201 Created**: The user has been successfully created, and authentication tokens are returned.
- **400 Bad Request**: The request body contains invalid data or is missing required fields.
- **401 Unauthorized**: The authentication or token validation has failed.

------

> [!IMPORTANT]
>
> - If a `personal_image` is provided, it will be saved as the user’s profile picture.
> - The `refresh` token can be used to obtain a new `access` token, ensuring the user remains authenticated without needing to log in again.
> - Ensure that your application is properly configured to handle image file uploads by setting up `MEDIA_URL` and `MEDIA_ROOT` in your Django settings.



------

### **Common Errors:**

- **400 Bad Request**: This occurs if required fields (e.g., username, password, email) are missing or invalid.
- **401 Unauthorized**: This happens if the user’s credentials are invalid, or the password does not meet the required validation criteria.

------

## **Friendship API Documentation**

**Endpoint:**

- **Base Path:** `/api/users/`
- **Endpoint Path:** `/api/users/friendship/`

#### **HTTP Methods:**

- **GET:** Retrieve all friendship relationships for the currently logged-in user.
- **POST:** Create a new friendship relationship.
- **PATCH:** Update the status of an existing friendship.

------

#### **GET Method** - Retrieve all friendships for the logged-in user

##### **Description:**

This endpoint retrieves all friendship relations where the logged-in user is either the sender or receiver. It returns a list of friendships along with their statuses.

##### **Response:**

###### **Success (200 OK):**

```json
[
  {
    "id": "<uuid of friendship>",
    "from_user": "uuid_of_from_user",
    "to_user": "uuid_of_to_user",
    "status_from_user": "status",
    "status_to_user": "status"
  },
  ...
]
```

###### **Error (401 Unauthorized):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

##### **Example Request:**

```http
GET /api/users/friendship/ HTTP/1.1
Authorization: Bearer <access_token>
```

------

#### **POST Method** - Create a new friendship

**Description:**

This endpoint allows a user to send a friendship request to another user. The request includes the `to_user` ID and an initial `status` for the requesting user.

**Request Body:**

```json
{
  "to_user": "uuid_of_to_user",
  "status": "pending"
}
```

- **`to_user`** (required): The UUID of the user to whom the friendship request is being sent.
- **`status`** (required): The status of the user sending the request. Possible values are `"pending"`, `"accepted"`, or `"rejected"`.

**Response:**

**Success (201 Created):**

```json
{
  "id": "uuid_of_friendship",
  "from_user": {
    "id": "uuid_of_from_user",
    "personal_image": "url_of_personal_image",
    "username": "username",
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email"
  },
  "to_user": {
    "id": "uuid_of_to_user",
    "personal_image": "url_of_personal_image",
    "username": "username",
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email"
  },
  "date_created": "date_time",
  "status_from_user": "pending",
  "status_to_user": "pending"
}
```

**Error (400 Bad Request):**

```json
{
  "detail": "Friendship already exists."
}
```

**Error (404 Not Found):**

```json
{
  "detail": "User not found."
}
```

**Example Request:**

```http
POST /api/users/friendship/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "to_user": "uuid_of_to_user",
  "status": "pending"
}
```

------

#### **PATCH Method** - Update the status of an existing friendship

**Description:**

This endpoint allows users to update the status of an existing friendship. A user can update the friendship status for themselves (as the sender or receiver).

**Request Body:**

```json
{
  "friendship_id": "uuid_of_friendship",
  "status": "accepted"
}
```

- **`friendship_id`** (required): The UUID of the friendship relationship to update.
- **`status`** (required): The new status of the friendship. Possible values are `"pending"`, `"accepted"`, or `"rejected"`.

##### **Response:**

**Success (200 OK):**

```json
{
  "id": "uuid_of_friendship",
  "from_user": {
    "id": "uuid_of_from_user",
    "personal_image": "url_of_personal_image",
    "username": "username",
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email"
  },
  "to_user": {
    "id": "uuid_of_to_user",
    "personal_image": "url_of_personal_image",
    "username": "username",
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email"
  },
  "date_created": "date_time",
  "status_from_user": "pending",
  "status_to_user": "pending"
}
```

###### **Error (400 Bad Request):**

```json
{
  "detail": "Invalid status."
}
```

**Error (403 Forbidden):**

```json
{
  "detail": "You are not authorized to update this friendship."
}
```

###### **Error (404 Not Found):**

```json
{
  "detail": "Friendship not found."
}
```

#### **Example Request:**

```http
PATCH /api/users/friendship/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "friendship_id": "uuid_of_friendship",
  "status": "accepted"
}
```

------

> [!IMPORTANT]
>
> ### **Important Notes:**
>
> - **Authentication:** All methods require the user to be authenticated, with valid credentials.
> - **Authorization:** For `PATCH` requests, the user must be the owner of one side of the friendship (either `from_user` or `to_user`) to update the status.
> - Status Values:
>   - `"pending"`: The default status when a user sends a friend request.
>   - `"accepted"`: The status when both users agree to the friendship.
>   - `"rejected"`: The status when a friendship request is declined.

Here is the updated API documentation for both the `UserProfileView` and `UserListView`:

------

## **UserProfileView API Documentation**

### **Endpoint:**

- **Base Path:** `/api/users/`
- **Endpoint Path:** `/api/users/profile/`
- **HTTP Method:** `GET`, `PATCH`

### **Description:**

The `UserProfileView` API allows authenticated users to view and update their profile information.

- **GET**: Retrieve the profile information of the currently authenticated user.
- **PATCH**: Update the profile of the currently authenticated user. Only the fields provided in the request body will be updated.

### **Permissions:**

- **IsAuthenticated**: Only authenticated users can access or modify their profile information.

### **Request Body (PATCH):**

For **PATCH** requests, the body should include the fields to be updated. The request should be `application/json`:

```json
{
  "first_name": "string",      // (optional) The updated first name of the user.
  "last_name": "string",       // (optional) The updated last name of the user.
  "personal_image": "file"     // (optional) The updated profile image (image file in formats such as .jpg, .png).
}
```

### **Response:**

#### **GET Response Example (Success):**

```json
{
  "id": "string",               // (string) The unique identifier for the user.
  "username": "string",         // (string) The user's username.
  "email": "string",            // (string) The user's email address.
  "first_name": "string",       // (string) The user's first name.
  "last_name": "string",        // (string) The user's last name.
  "personal_image": "string"    // (string) The URL of the user's profile image.
}
```

#### **PATCH Response Example (Success):**

```json
{
  "id": "string",               // (string) The unique identifier for the user.
  "username": "string",         // (string) The user's username.
  "email": "string",            // (string) The user's email address.
  "first_name": "string",       // (string) The updated first name of the user.
  "last_name": "string",        // (string) The updated last name of the user.
  "personal_image": "string"    // (string) The URL of the updated profile image.
}
```

#### **Error (400 Bad Request):**

```json
{
  "error": "string"             // (string) Description of the error (e.g., invalid data, missing fields).
}
```

### **Request Examples:**

#### **GET Request:**

```http
GET /api/users/profile/ HTTP/1.1
Authorization: Bearer <access_token>
```

#### **PATCH Request:**

```http
PATCH /api/users/profile/ HTTP/1.1
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "first_name": "UpdatedFirstName",
  "last_name": "UpdatedLastName"
}
```

### **Response Example (Error):**

```json
{
  "error": "Invalid data provided."
}
```

### **Field Descriptions:**

- **`first_name`** (optional): The updated first name of the user.
- **`last_name`** (optional): The updated last name of the user.
- **`personal_image`** (optional): A profile image for the user. Accepts image files (e.g., .jpg, .png).

### **Response Status Codes:**

- **200 OK**: The user’s profile data has been successfully retrieved or updated.
- **400 Bad Request**: Invalid data or missing fields in the request.
- **401 Unauthorized**: The user is not authenticated or the authentication token is invalid.

------

## **UserListView API Documentation**

### **Endpoint:**

- **Base Path:** `/api/users/`
- **Endpoint Path:** `/api/users/`
- **HTTP Method:** `GET`

### **Description:**

The `UserListView` allows authenticated users to retrieve a list of users. The list is paginated and can be filtered by the `username` query parameter. The response includes specific fields for each user, including their `id`, `username`, and optional `personal_image`.

- **GET**: Retrieve a paginated list of users. Optionally, filter users by the `username` query parameter.

### **Permissions:**

- **IsAuthenticated**: Only authenticated users can access the list of users.

### **Request Parameters:**

#### **Query Parameters:**

- **`username`** (optional): A string to filter the users by username. This query parameter can be used to search for users whose username contains the provided value.
- **`page_size`** (optional): The number of users to display per page. The default value is `10`, but you can override it using the `page_size` query parameter, with a maximum of `100`.

#### **Example Request:**

```http
GET /api/users/?username=john&page_size=20 HTTP/1.1
Authorization: Bearer <access_token>
```

### **Response:**

#### **Response Example (Success):**

```json
{
  "count": 2,                               // (integer) The total number of users matching the filter criteria.
  "next": "http://example.com/api/users/?page=2",  // (string) The URL for the next page of results.
  "previous": null,                        // (string) The URL for the previous page of results (if available).
  "results": [
    {
      "id": "string",                       // (string) The unique identifier for the user.
      "username": "john_doe",               // (string) The user's username.
      "personal_image": "string"            // (string) The URL of the user's profile image (if available).
    },
    {
      "id": "string",                       // (string) The unique identifier for the user.
      "username": "john_smith",             // (string) The user's username.
      "personal_image": "string"            // (string) The URL of the user's profile image (if available).
    }
  ]
}
```

#### **Error (400 Bad Request):**

```json
{
  "error": "Invalid query parameters."     // (string) Description of the error, such as invalid query parameters.
}
```

### **Response Status Codes:**

- **200 OK**: The list of users has been successfully retrieved.
- **400 Bad Request**: The query parameters are invalid or malformed.
- **401 Unauthorized**: The user is not authenticated or the authentication token is invalid.

### **Pagination:**

The response includes pagination information to allow clients to navigate through the list of users:

- **`count`**: The total number of users available (not limited by pagination).

- **`next`**: The URL for the next page of results (if available).

- **`previous`**: The URL for the previous page of results (if available).

- `results`

  : The list of users in the current page. Each user includes:

  - **`id`**: The unique identifier for the user.
  - **`username`**: The user's username.
  - **`personal_image`**: The URL of the user's profile image (if available).

### **Field Descriptions:**

- **`id`**: The unique identifier for each user.
- **`username`**: The username of the user.
- **`personal_image`**: The URL to the user's profile image (if available).

------

## **MessageStatusView API Documentation**

### **Endpoint:**

- **Base Path:** `/api/messages/status/`
- **Endpoint Path:** `/friendship/<uuid:friendship_id>/messages/`
- **HTTP Method:** `GET`

### **Description:**

The `MessageStatusView` retrieves a paginated list of message statuses related to a specific friendship. It allows users to filter the message statuses by various query parameters, such as `start_date`, `start_message_id`, `after`, and `before`. The API ensures that the requesting user is part of the friendship, and only valid filters are applied.

### **Permissions:**

- **IsAuthenticated**: Only authenticated users can access the message status information.

### **Request Parameters:**

#### **URL Parameters:**

- **`friendship_id`** (required): The unique identifier of the friendship for which the message statuses are being retrieved.

#### **Query Parameters:**

- **`after`** (optional): A flag to retrieve statuses after a specified date or message.
- **`before`** (optional): A flag to retrieve statuses before a specified date or message.
- **`start_date`** (optional): A filter to retrieve statuses created on or after/before a given date.
- **`message_id`** (optional): A filter to retrieve statuses related to a specific message ID.

#### **Example Request:**

```http
GET /api/messages/status/1/?after=true&start_date=2024-12-20 HTTP/1.1
Authorization: Bearer <access_token>
```

### **Response:**

#### **Response Example (Success):**

```json
{
  "count": 2,                               // (integer) Total number of message statuses available.
  "next": "http://example.com/api/messages/status/1/?page=2",  // (string) URL for the next page of results.
  "previous": null,                         // (string) URL for the previous page of results (if applicable).
  "results": [
    {
      "id": "string",                       // (string) The unique identifier for the message status.
      "message": {
        "id": "string",                     // (string) The unique identifier for the message.
        "sender": "string",                  // (string) Sender of the message.
        "created_at": "string"               // (string) The timestamp when the message was created.
      },
      "is_received": true                    // (boolean) Whether the message has been received.
    },
    {
      "id": "string",                       // (string) The unique identifier for the message status.
      "message": {
        "id": "string",                     // (string) The unique identifier for the message.
        "sender": "string",                  // (string) Sender of the message.
        "created_at": "string"               // (string) The timestamp when the message was created.
      },
      "is_received": false                   // (boolean) Whether the message has been received.
    }
  ]
}
```

#### **Error (400 Bad Request):**

```json
{
  "error": "Invalid query parameters."     // (string) Description of the error, such as invalid query parameters.
}
```

#### **Error (404 Not Found):**

```json
{
  "error": "Friendship not found."        // (string) Description of the error if the friendship does not exist.
}
```

### **Response Status Codes:**

- **200 OK**: The list of message statuses has been successfully retrieved.
- **400 Bad Request**: The query parameters are invalid or malformed.
- **404 Not Found**: The requested friendship could not be found or the user is not part of the friendship.
- **401 Unauthorized**: The user is not authenticated or the authentication token is invalid.

### **Pagination:**

The response includes pagination information to navigate through the list of message statuses:

- **`count`**: The total number of message statuses available (not limited by pagination).

- **`next`**: The URL for the next page of results (if available).

- **`previous`**: The URL for the previous page of results (if available).

- `results`

  : The list of message statuses for the current page. Each status includes:

  - **`id`**: The unique identifier for the message status.

  - ```
    message
    ```

    :

    - **`id`**: The unique identifier for the associated message.
    - **`sender`**: The user who sent the message.
    - **`created_at`**: The timestamp when the message was created.

  - **`is_received`**: A boolean indicating whether the message has been received.

.

------





# Database diagram

![Image Description](readme_images/databasemodel.svg)

# user application end points
![Image Description](readme_images/endpoint.svg)
