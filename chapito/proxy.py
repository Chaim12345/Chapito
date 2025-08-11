import json
from typing import Callable, List, Optional, Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

import time
import uuid
from pydantic import BaseModel, field_validator
import uvicorn
import logging

from chapito.config import Config


async def generate_json_stream(data: dict):
    """Generate streaming response in OpenAI-compatible format."""
    # Remove the message field and add delta for streaming
    if "message" in data["choices"][0]:
        data["choices"][0]["delta"] = data["choices"][0]["message"]
        del data["choices"][0]["message"]
    
    yield f"data: {json.dumps(data)}\n\n"
    yield "data: [DONE]\n\n"


class Message(BaseModel):
    """OpenAI-compatible message model."""
    role: str
    content: Union[str, List[dict]]

    @field_validator("content", mode="before")
    def transform_content(cls, value):
        if isinstance(value, list):
            text_parts = [item["text"] for item in value if item.get("type") == "text"]
            return "\n\n".join(text_parts)
        return value


class ChatRequest(BaseModel):
    """OpenAI-compatible chat completion request model."""
    model: str
    messages: List[Message]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stream: Optional[bool] = False
    n: Optional[int] = 1
    stop: Optional[Union[str, List[str]]] = None
    user: Optional[str] = None


class ChatCompletionChoice(BaseModel):
    """OpenAI-compatible choice model."""
    index: int
    message: dict
    finish_reason: str


class ChatCompletionUsage(BaseModel):
    """OpenAI-compatible usage model."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response model."""
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage


class ErrorResponse(BaseModel):
    """OpenAI-compatible error response model."""
    error: dict


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str


class ModelsResponse(BaseModel):
    """Models list response model."""
    object: str
    data: List[dict]


app = FastAPI(
    title="Chapito OpenAI-Compatible API",
    description="A proxy API that provides OpenAI-compatible endpoints for various AI chatbots",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

last_chat_messages: List[str] = []


def find_index_from_end(lst: List[Message], values: List[str]) -> int:
    """Find the index of the last message that matches any value in the list."""
    for i in range(len(lst) - 1, -1, -1):
        message = lst[i]
        if message.content.strip() in values:
            return i
    return -1


def custom_openapi():
    """Custom OpenAPI schema to match OpenAI's API structure."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Chapito OpenAI-Compatible API",
        version="1.0.0",
        description="A proxy API that provides OpenAI-compatible endpoints for various AI chatbots",
        routes=app.routes,
    )
    
    # Customize the schema to match OpenAI's structure
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/Yajusta/Chapito/main/chapito.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors with OpenAI-compatible format."""
    return JSONResponse(
        status_code=404, 
        content={
            "error": {
                "message": "The requested resource was not found",
                "type": "not_found",
                "param": None,
                "code": "not_found"
            }
        }
    )


@app.exception_handler(422)
async def validation_error_handler(request: Request, exc: HTTPException):
    """Handle validation errors with OpenAI-compatible format."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "message": "Invalid request parameters",
                "type": "invalid_request_error",
                "param": None,
                "code": "invalid_request_error"
            }
        }
    )


@app.get("/models", response_model=ModelsResponse, tags=["Models"])
async def get_models():
    """Get available models in OpenAI-compatible format."""
    return {
        "object": "list",
        "data": [
            {
                "id": "chapito",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "chapito",
                "permission": [],
                "root": "chapito",
                "parent": None
            }
        ]
    }


@app.post("/chat/completions", response_model=Union[ChatCompletionResponse, ErrorResponse], tags=["Chat"])
async def chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint."""
    global last_chat_messages

    logging.debug(f"Request received: {request}")

    # Validate request
    if not request.messages:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": {
                    "message": "Field 'messages' is missing or empty",
                    "type": "invalid_request_error",
                    "param": "messages",
                    "code": "invalid_request_error"
                }
            }
        )
    
    if len(request.messages) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": "At least one message is required",
                    "type": "invalid_request_error",
                    "param": "messages",
                    "code": "invalid_request_error"
                }
            }
        )

    try:
        # Process messages
        last_relevant_message_position = -2 if len(request.messages) >= 2 else -1
        if len(request.messages) > 0:
            logging.debug(f"Last relevant message in request: {request.messages[last_relevant_message_position]}")

        index_of_last_message = find_index_from_end(request.messages, last_chat_messages)
        prompt = "\n\n".join(
            f"[{message.role}] {message.content}" for message in request.messages[index_of_last_message + 1 :]
        )
        last_chat_messages.append(request.messages[-1].content.strip())
        
        if not prompt:
            logging.debug("Can't determine latest messages, sending the whole chat session")
            prompt = "\n\n".join(f"[{message.role}] {message.content}" for message in request.messages)

        # Get response from chatbot
        response_content = app.state.send_request_and_get_response(app.state.driver, prompt)
        if response_content:
            last_chat_messages.append(response_content)
        
        logging.debug(f"Response from chat ends with: {response_content[-100:]}")
        logging.debug("Sending response")

        # Prepare response data
        data = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant", 
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(prompt.split()) + len(response_content.split())
            }
        }

        # Handle streaming
        if request.stream or app.state.config.stream:
            logging.debug("Send StreamingResponse")
            return StreamingResponse(
                generate_json_stream(data), 
                media_type="text/event-stream"
            )
        else:
            logging.debug("Send JSONResponse")
            return JSONResponse(data)

    except Exception as e:
        logging.error(f"Error in chat_completions: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Internal server error: {str(e)}",
                    "type": "server_error",
                    "param": None,
                    "code": "internal_error"
                }
            }
        )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chapito-proxy"}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information."""
    return {
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


@app.get("/v1", tags=["Root"])
async def v1_root():
    """OpenAI v1 endpoint providing API information."""
    return {
        "name": "Chapito OpenAI-Compatible API",
        "version": "1.0.0",
        "description": "A proxy API that provides OpenAI-compatible endpoints for various AI chatbots",
        "endpoints": {
            "models": "/v1/models",
            "chat_completions": "/v1/chat/completions",
            "health": "/v1/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "compatibility": "OpenAI API v1"
    }


@app.get("/v1/models", response_model=ModelsResponse, tags=["Models"])
async def v1_get_models():
    """Get available models in OpenAI-compatible format (v1 endpoint)."""
    return {
        "object": "list",
        "data": [
            {
                "id": "chapito",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "chapito",
                "permission": [],
                "root": "chapito",
                "parent": None
            }
        ]
    }


@app.post("/v1/chat/completions", response_model=Union[ChatCompletionResponse, ErrorResponse], tags=["Chat"])
async def v1_chat_completions(request: ChatRequest):
    """OpenAI-compatible chat completions endpoint (v1 endpoint)."""
    global last_chat_messages

    logging.debug(f"Request received: {request}")

    # Validate request
    if not request.messages:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": {
                    "message": "Field 'messages' is missing or empty",
                    "type": "invalid_request_error",
                    "param": "messages",
                    "code": "invalid_request_error"
                }
            }
        )
    
    if len(request.messages) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "message": "At least one message is required",
                    "type": "invalid_request_error",
                    "param": "messages",
                    "code": "invalid_request_error"
                }
            }
        )

    try:
        # Process messages
        last_relevant_message_position = -2 if len(request.messages) >= 2 else -1
        if len(request.messages) > 0:
            logging.debug(f"Last relevant message in request: {request.messages[last_relevant_message_position]}")

        index_of_last_message = find_index_from_end(request.messages, last_chat_messages)
        prompt = "\n\n".join(
            f"[{message.role}] {message.content}" for message in request.messages[index_of_last_message + 1 :]
        )
        last_chat_messages.append(request.messages[-1].content.strip())
        
        if not prompt:
            logging.debug("Can't determine latest messages, sending the whole chat session")
            prompt = "\n\n".join(f"[{message.role}] {message.content}" for message in request.messages)

        # Get response from chatbot
        response_content = app.state.send_request_and_get_response(app.state.driver, prompt)
        if response_content:
            last_chat_messages.append(response_content)
        
        logging.debug(f"Response from chat ends with: {response_content[-100:]}")
        logging.debug("Sending response")

        # Prepare response data
        data = {
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant", 
                        "content": response_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response_content.split()),
                "total_tokens": len(prompt.split()) + len(response_content.split())
            }
        }

        # Handle streaming
        if request.stream or app.state.config.stream:
            logging.debug("Send StreamingResponse")
            return StreamingResponse(
                generate_json_stream(data), 
                media_type="text/event-stream"
            )
        else:
            logging.debug("Send JSONResponse")
            return JSONResponse(data)

    except Exception as e:
        logging.error(f"Error in chat_completions: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Internal server error: {str(e)}",
                    "type": "server_error",
                    "param": None,
                    "code": "internal_error"
                }
            }
        )


@app.get("/v1/health", response_model=HealthResponse, tags=["Health"])
async def v1_health_check():
    """Health check endpoint (v1 endpoint)."""
    return {"status": "healthy", "service": "chapito-proxy"}


@app.get("/openapi.json", tags=["API"])
async def get_openapi_json():
    """Get the OpenAPI specification in JSON format."""
    return app.openapi()


def init_proxy(driver, send_request_and_get_response: Callable, config: Config) -> None:
    """Initialize the proxy with driver and configuration."""
    app.state.driver = driver
    app.state.send_request_and_get_response = send_request_and_get_response
    app.state.config = config

    logging.debug(f"Listening on: {config.host}:{config.port}")

    uvicorn.run(app, host=config.host, port=config.port)
