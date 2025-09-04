"""
Anthropic API Client - Local API Server
A FastAPI application that provides a complete REST API interface to the Anthropic SDK
"""

import os
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import anthropic
from typing import Optional, List, Dict, Any, Union
import time
from app.streaming import create_streaming_response
from app.models_api import get_model_info, list_models
from app.batches_api import (
    create_batch, retrieve_batch, list_batches,
    cancel_batch, delete_batch, get_batch_results
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global Anthropic client instances
anthropic_client: Optional[anthropic.Anthropic] = None
async_anthropic_client: Optional[anthropic.AsyncAnthropic] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown"""
    global anthropic_client, async_anthropic_client

    # Startup
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable is required")
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    # Initialize clients
    anthropic_client = anthropic.Anthropic(api_key=api_key)
    async_anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)

    logger.info("Anthropic API clients initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down Anthropic API server")

# Create FastAPI application
app = FastAPI(
    title="Anthropic API Client",
    description="A complete REST API interface to the Anthropic SDK for local deployment",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your local network
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class MessageRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    max_tokens: int = 1024
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    system: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None

class MessageResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TokenCountRequest(BaseModel):
    model: str
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None

class TokenCountResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BatchRequest(BaseModel):
    requests: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str
    version: str
    clients_initialized: bool

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s"
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            method=request.method,
            url=str(request.url),
            error=str(e),
            process_time=f"{process_time:.3f}s"
        )
        raise

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        clients_initialized=anthropic_client is not None and async_anthropic_client is not None
    )

@app.post("/api/v1/messages/create", response_model=MessageResponse)
async def create_message(request: MessageRequest):
    """Create a message using the Anthropic API"""
    try:
        if not anthropic_client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        # Prepare request parameters
        params = {
            "model": request.model,
            "messages": request.messages,
            "max_tokens": request.max_tokens,
        }

        # Add optional parameters if provided
        if request.temperature is not None:
            params["temperature"] = request.temperature
        if request.top_p is not None:
            params["top_p"] = request.top_p
        if request.top_k is not None:
            params["top_k"] = request.top_k
        if request.stop_sequences:
            params["stop_sequences"] = request.stop_sequences
        if request.system:
            params["system"] = request.system
        if request.metadata:
            params["metadata"] = request.metadata
        if request.tools:
            params["tools"] = request.tools
        if request.tool_choice:
            params["tool_choice"] = request.tool_choice

        start_time = time.time()
        message = anthropic_client.messages.create(**params)
        process_time = time.time() - start_time

        logger.info(
            "Message created successfully",
            model=request.model,
            input_tokens=getattr(message.usage, 'input_tokens', None),
            output_tokens=getattr(message.usage, 'output_tokens', None),
            process_time=f"{process_time:.3f}s"
        )

        return MessageResponse(
            success=True,
            data={
                "id": message.id,
                "type": message.type,
                "role": message.role,
                "content": [content.model_dump() for content in message.content],
                "model": message.model,
                "stop_reason": message.stop_reason,
                "stop_sequence": message.stop_sequence,
                "usage": {
                    "input_tokens": getattr(message.usage, 'input_tokens', None),
                    "output_tokens": getattr(message.usage, 'output_tokens', None),
                    "cache_creation_input_tokens": getattr(message.usage, 'cache_creation_input_tokens', None),
                    "cache_read_input_tokens": getattr(message.usage, 'cache_read_input_tokens', None),
                } if message.usage else None
            },
            metadata={
                "request_id": getattr(message, '_request_id', None),
                "processing_time_ms": int(process_time * 1000)
            }
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in create_message", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/messages/count-tokens", response_model=TokenCountResponse)
async def count_tokens(request: TokenCountRequest):
    """Count tokens for a message without creating it"""
    try:
        if not anthropic_client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        params = {
            "model": request.model,
            "messages": request.messages,
        }

        if request.tools:
            params["tools"] = request.tools

        count = anthropic_client.messages.count_tokens(**params)

        return TokenCountResponse(
            success=True,
            data={
                "input_tokens": count.input_tokens,
                "cache_creation_input_tokens": getattr(count, 'cache_creation_input_tokens', 0),
                "cache_read_input_tokens": getattr(count, 'cache_read_input_tokens', 0),
            }
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in count_tokens", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in count_tokens", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/messages/stream")
async def stream_message(request: MessageRequest):
    """Stream a message response using Server-Sent Events"""
    try:
        if not async_anthropic_client:
            raise HTTPException(status_code=500, detail="Async Anthropic client not initialized")

        # Prepare request parameters
        params = {
            "model": request.model,
            "messages": request.messages,
            "max_tokens": request.max_tokens,
        }

        # Add optional parameters if provided
        if request.temperature is not None:
            params["temperature"] = request.temperature
        if request.top_p is not None:
            params["top_p"] = request.top_p
        if request.top_k is not None:
            params["top_k"] = request.top_k
        if request.stop_sequences:
            params["stop_sequences"] = request.stop_sequences
        if request.system:
            params["system"] = request.system
        if request.metadata:
            params["metadata"] = request.metadata
        if request.tools:
            params["tools"] = request.tools
        if request.tool_choice:
            params["tool_choice"] = request.tool_choice

        logger.info("Starting streaming response", model=request.model)

        return await create_streaming_response(async_anthropic_client, **params)

    except anthropic.APIError as e:
        logger.error("Anthropic API error in streaming", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in streaming", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Models endpoints
@app.get("/api/v1/models")
async def get_models_list():
    """List all available models"""
    return list_models(anthropic_client)

@app.get("/api/v1/models/{model_id}")
async def get_model(model_id: str):
    """Get information about a specific model"""
    return get_model_info(anthropic_client, model_id)

# Batch endpoints
@app.post("/api/v1/batches/create")
async def create_message_batch(request: BatchRequest):
    """Create a new message batch"""
    return create_batch(anthropic_client, request.requests)

@app.get("/api/v1/batches/{batch_id}")
async def get_batch(batch_id: str):
    """Retrieve a specific batch"""
    return retrieve_batch(anthropic_client, batch_id)

@app.get("/api/v1/batches")
async def get_batches_list(limit: int = 20):
    """List all batches"""
    return list_batches(anthropic_client, limit)

@app.post("/api/v1/batches/{batch_id}/cancel")
async def cancel_message_batch(batch_id: str):
    """Cancel a batch"""
    return cancel_batch(anthropic_client, batch_id)

@app.delete("/api/v1/batches/{batch_id}")
async def delete_message_batch(batch_id: str):
    """Delete a batch"""
    return delete_batch(anthropic_client, batch_id)

@app.get("/api/v1/batches/{batch_id}/results")
async def get_message_batch_results(batch_id: str):
    """Get batch results"""
    return await get_batch_results(anthropic_client, batch_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
