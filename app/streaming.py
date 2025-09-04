"""
Streaming functionality for Anthropic API using Server-Sent Events (SSE)
"""

import json
import asyncio
from typing import Dict, Any, AsyncGenerator
import anthropic
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import structlog

logger = structlog.get_logger()

class SSEManager:
    """Manages Server-Sent Events for streaming responses"""

    def __init__(self, async_client: anthropic.AsyncAnthropic):
        self.async_client = async_client

    async def stream_message_events(self, **params) -> AsyncGenerator[str, None]:
        """Stream message events as SSE"""
        try:
            async with self.async_client.messages.stream(**params) as stream:
                async for event in stream:
                    # Convert event to SSE format
                    event_data = self._format_event(event)
                    yield f"data: {json.dumps(event_data)}\n\n"

                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)

        except Exception as e:
            logger.error("Error in streaming", error=str(e))
            error_event = {
                "type": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    def _format_event(self, event) -> Dict[str, Any]:
        """Format Anthropic event for SSE"""
        if hasattr(event, 'type'):
            event_type = event.type

            if event_type == "text":
                return {
                    "type": "text",
                    "text": event.text,
                    "snapshot": getattr(event, 'snapshot', '')
                }

            elif event_type == "input_json":
                return {
                    "type": "input_json",
                    "partial_json": getattr(event, 'partial_json', ''),
                    "snapshot": getattr(event, 'snapshot', '')
                }

            elif event_type == "content_block_start":
                return {
                    "type": "content_block_start",
                    "index": event.index,
                    "content_block": {
                        "type": event.content_block.type,
                        "text": getattr(event.content_block, 'text', ''),
                        "id": getattr(event.content_block, 'id', None),
                        "name": getattr(event.content_block, 'name', None),
                        "input": getattr(event.content_block, 'input', None)
                    }
                }

            elif event_type == "content_block_delta":
                return {
                    "type": "content_block_delta",
                    "index": event.index,
                    "delta": {
                        "type": event.delta.type,
                        "text": getattr(event.delta, 'text', ''),
                        "partial_json": getattr(event.delta, 'partial_json', '')
                    }
                }

            elif event_type == "content_block_stop":
                return {
                    "type": "content_block_stop",
                    "index": event.index,
                    "content_block": event.content_block.model_dump() if hasattr(event, 'content_block') else None
                }

            elif event_type == "message_start":
                return {
                    "type": "message_start",
                    "message": {
                        "id": event.message.id,
                        "type": event.message.type,
                        "role": event.message.role,
                        "model": event.message.model,
                        "content": [],
                        "stop_reason": None,
                        "stop_sequence": None,
                        "usage": {
                            "input_tokens": getattr(event.message.usage, 'input_tokens', 0),
                            "output_tokens": getattr(event.message.usage, 'output_tokens', 0),
                            "cache_creation_input_tokens": getattr(event.message.usage, 'cache_creation_input_tokens', 0),
                            "cache_read_input_tokens": getattr(event.message.usage, 'cache_read_input_tokens', 0),
                        } if hasattr(event.message, 'usage') and event.message.usage else {
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "cache_creation_input_tokens": 0,
                            "cache_read_input_tokens": 0,
                        }
                    }
                }

            elif event_type == "message_delta":
                return {
                    "type": "message_delta",
                    "delta": {
                        "stop_reason": getattr(event.delta, 'stop_reason', None),
                        "stop_sequence": getattr(event.delta, 'stop_sequence', None)
                    },
                    "usage": {
                        "output_tokens": getattr(event, 'usage', {}).get('output_tokens', 0)
                    } if hasattr(event, 'usage') else {"output_tokens": 0}
                }

            elif event_type == "message_stop":
                return {
                    "type": "message_stop",
                    "message": event.message.model_dump() if hasattr(event, 'message') else None
                }

            elif event_type == "ping":
                return {
                    "type": "ping"
                }

            else:
                return {
                    "type": event_type,
                    "data": str(event)
                }
        else:
            return {
                "type": "unknown",
                "data": str(event)
            }

async def create_streaming_response(async_client: anthropic.AsyncAnthropic, **params):
    """Create a streaming response for the Anthropic API"""
    if not async_client:
        raise HTTPException(status_code=500, detail="Async Anthropic client not initialized")

    sse_manager = SSEManager(async_client)

    return StreamingResponse(
        sse_manager.stream_message_events(**params),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )
