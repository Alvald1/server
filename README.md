# Secure Message Server

A server application for securely exchanging encrypted messages between clients using RSA encryption and temporary session keys.

## Overview

This application implements a secure communication channel with the following components:
- RSA key generation and management
- Message encryption and decryption using hybrid RSA/AES encryption
- FastAPI HTTP server for client-server communication
- Redis for temporary data storage
- MySQL integration for user authentication and device management

## System Requirements

- Python 3.7+
- Redis server (running on port 6581)
- MySQL database with WordPress user data
- Required Python packages (see Installation)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd server
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn redis mysql-connector-python python-dotenv phpserialize cryptography python-multipart
```

3. Configure environment variables by creating a `.env` file:
```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
```

4. Start the server:
```bash
uvicorn http_post_listner:app --host 0.0.0.0 --port 8000
```

## Architecture

### File Structure

- `http_post_listner.py` - FastAPI server implementation that handles client requests
- `rsa_manager.py` - RSA encryption/decryption utilities and key management
- `mysql_site.py` - Database interactions for user authentication and device management

### Data Flow

1. Client requests authentication with a unique key (user_id + device_id)
2. Server validates the user against MySQL database
3. If valid, server generates RSA key pair and stores in Redis
4. Client encrypts messages using the server's public key
5. Server decrypts messages using the stored private key
6. Processed data is stored in Redis with SHA-256 hash identifiers

## API Endpoints

The server exposes a single POST endpoint at `/api` that handles different operations based on the provided parameters:

### Authentication Request

**Request:**
```
POST /api
Form Data:
  - key: <user_id><device_id>
  - status: "on"
```

**Responses:**
- Success: `{"message": "<public_key>", "code": 0, "name": "<device_name>"}`
- Already authenticated: `{"message": "already auth", "code": 1}`
- User/device not found: `{"message": "not found", "code": 2}`

### Logout Request

**Request:**
```
POST /api
Form Data:
  - key: <user_id><device_id>
  - status: "off"
```

**Responses:**
- Success: `{"message": "deleted", "code": 0}`
- Not found: `{"message": "not found", "code": 2}`

### Message Submission

**Request:**
```
POST /api
Form Data:
  - key: <user_id><device_id>
  - message: <encrypted_json_data>
```

**Responses:**
- Success: `{"message": "delivered", "code": 0}`
- Duplicate message: `{"message": "duplicate", "code": 1}`
- Not authenticated: `{"message": "not found", "code": 2}`

## Security Features

- **Hybrid Encryption**: Uses RSA for key exchange and AES for message encryption
- **Session-based Authentication**: Each client receives a unique RSA key pair
- **Message Integrity**: Prevents duplicate message submission
- **Database Integration**: Validates users against existing WordPress user database

## Message Format

The encrypted message should contain a JSON object with:
- `encryptedKey`: Base64-encoded RSA-encrypted AES key
- `iv`: Base64-encoded initialization vector for AES-CBC
- `ciphertext`: Base64-encoded encrypted message
- `minute`: Timestamp for message tracking

## Redis Structure

The system uses two Redis databases:
- DB 1 (`main_redis`): Stores encrypted messages with SHA-256 hash keys
- DB 2 (`auth_redis`): Stores authentication information and RSA keys for active sessions

## WordPress Integration

The system integrates with a WordPress database for user management:
- Validates user UUIDs against `wp_usermeta` table
- Tracks device connection status in serialized PHP format
- Updates device status on login/logout
