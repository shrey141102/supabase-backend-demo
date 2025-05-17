# Bitespeed Identity Reconciliation API

A Flask API that reconciles customer identities based on common contact information.

## Overview

This API implements the Bitespeed Backend Task for contact identity reconciliation. It tracks customer identities across multiple purchases by linking contacts with shared email addresses or phone numbers.

## Features

- Identity reconciliation based on common email or phone number
- Primary/secondary contact hierarchy
- Consolidated contact information in responses
- Support for PostgreSQL through Supabase

## Endpoints

### Health Check

```
GET /health
```
Returns the health status of the API.

### Identity Reconciliation
```
POST /identify
```
Accepts a JSON payload with email and/or phone number, and returns consolidated contact information.

**Request Format**:
```json
{
  "email": "example@example.com",
  "phoneNumber": "1234567890"
}
```

**Response Format**:
```json
{
  "contact": {
    "primaryContatctId": 1,
    "emails": ["example@example.com"],
    "phoneNumbers": ["1234567890"],
    "secondaryContactIds": []
  }
}
```

## Deployment

This API is deployed on Render.com and can be accessed at:

```
https://bitespeed-identity.onrender.com
```

## Local Development

1. Clone the repository
2. Set up a virtual environment
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your database connection details
5. Run the application
   ```
   python app.py
   ```

## Database

The application uses PostgreSQL via Supabase for production, and can fall back to SQLite for local development.

## License

This project is licensed under the MIT License - see the LICENSE file for details.