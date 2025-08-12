# Chapito API Documentation

## Overview

Chapito provides two API interfaces:

1. **Main API** (`main.py`) - A simplified chat interface for direct chatbot access
2. **Proxy API** (`chapito/proxy.py`) - An OpenAI-compatible API for seamless integration

## Main API (`main.py`)

The main API provides a simple interface for chatting with various AI models.

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Chat Endpoint
**POST** `/chat`

Send a message to any supported AI model.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "model": "gpt"
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "model": "gpt",
  "success": true,
  "error": null
}
```

#### 2. Get Available Models
**GET** `/models`

**Response:**
```json
{
  "supported_models": [
    "gpt",
    "claude",
    "grok",
    "ai_studio",
    "deepseek",
    "duckduckgo",
    "gemini",
    "kimi",
    "mistral",
    "perplexity",
    "qwen"
  ]
}
```

#### 3. Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "browser": "connected"
}
```

#### 4. Restart Browser
**POST** `/restart`

**Response:**
```json
{
  "message": "Browser restarted successfully"
}
```

#### 5. API Information
**GET** `/`

**Response:**
```json
{
  "name": "Chapito API",
  "version": "1.0.0",
  "description": "Free API access using web-based chatbots",
  "endpoints": {
    "chat": "/chat",
    "models": "/models",
    "health": "/health",
    "restart": "/restart",
    "docs": "/docs",
    "redoc": "/redoc",
    "openapi": "/openapi.json"
  }
}
```

## Proxy API (`chapito/proxy.py`)

The proxy API is designed to be fully compatible with OpenAI's API, allowing you to use existing OpenAI client libraries without modification.

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Chat Completions
**POST** `/chat/completions`

This endpoint follows the exact same format as OpenAI's chat completions API.

**Request Body:**
```json
{
  "model": "chapito",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "chapito",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! I'm doing well, thank you for asking. How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

#### 2. Models List
**GET** `/models`

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "chapito",
      "object": "model",
      "created": 1677652288,
      "owned_by": "chapito",
      "permission": [],
      "root": "chapito",
      "parent": null
    }
  ]
}
```

#### 3. Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "chapito-proxy"
}
```

#### 4. API Information
**GET** `/`

**Response:**
```json
{
  "name": "Chapito OpenAI-Compatible API",
  "version": "1.0.0",
  "description": "A proxy API that provides OpenAI-compatible endpoints for various AI chatbots",
  "endpoints": {
    "models": "/models",
    "chat_completions": "/chat/completions",
    "health": "/health",
    "docs": "/docs",
    "redoc": "/redoc",
    "openapi": "/openapi.json"
  },
  "compatibility": "OpenAI API v1"
}
```

## OpenAPI Documentation

Both APIs provide automatic OpenAPI documentation:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## Usage Examples

### Using the Main API

```python
import requests

# Send a chat message
response = requests.post("http://localhost:8000/chat", json={
    "message": "What is the capital of France?",
    "model": "gpt"
})

print(response.json()["response"])
```

### Using the Proxy API (OpenAI-compatible)

```python
import openai

# Configure the client to use Chapito
openai.api_base = "http://localhost:8000"
openai.api_key = "dummy-key"  # Not used by Chapito

# Send a chat completion request
response = openai.ChatCompletion.create(
    model="chapito",
    messages=[
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
```

### Using with cURL

#### Main API
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "gpt"
  }'
```

#### Proxy API
```bash
curl -X POST "http://localhost:8000/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chapito",
    "messages": [
      {
        "role": "user",
        "content": "Hello, how are you?"
      }
    ]
  }'
```

## Error Handling

Both APIs return consistent error responses:

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "param": "parameter_name",
    "code": "error_code"
  }
}
```

### Common Error Types

- `invalid_request_error` - Invalid request parameters
- `not_found` - Resource not found
- `server_error` - Internal server error

## Configuration

The APIs can be configured through the `config.ini` file or command-line arguments:

```ini
[DEFAULT]
host = 0.0.0.0
port = 8000
stream = false
```

## CORS Support

Both APIs include CORS middleware to support cross-origin requests from web applications.

## Streaming Support

The proxy API supports streaming responses when `stream: true` is set in the request:

```json
{
  "model": "chapito",
  "messages": [
    {"role": "user", "content": "Tell me a story"}
  ],
  "stream": true
}
```

## Compatibility Notes

- The proxy API is designed to be a drop-in replacement for OpenAI's API
- All standard OpenAI parameters are supported (temperature, max_tokens, etc.)
- The `model` parameter should be set to "chapito" for the proxy API
- Streaming responses follow the same Server-Sent Events format as OpenAI

## Getting Started

1. Start the API server:
   ```bash
   python main.py  # For main API
   # or
   python -c "from chapito.proxy import init_proxy; init_proxy(driver, func, config)"  # For proxy API
   ```

2. Access the API documentation at `/docs`

3. Start making requests to the endpoints

4. For OpenAI compatibility, use the proxy API endpoints