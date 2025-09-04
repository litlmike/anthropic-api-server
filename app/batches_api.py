"""
Batch processing API endpoints for Anthropic SDK
"""

from fastapi import HTTPException
import anthropic
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

class BatchCreateResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BatchRetrieveResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BatchListResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class BatchCancelResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BatchDeleteResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BatchResultsResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def create_batch(client: anthropic.Anthropic, requests: List[Dict[str, Any]]) -> BatchCreateResponse:
    """Create a new message batch"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        batch = client.messages.batches.create(requests=requests)

        return BatchCreateResponse(
            success=True,
            data={
                "id": batch.id,
                "type": batch.type,
                "processing_status": getattr(batch, 'processing_status', None),
                "request_counts": getattr(batch, 'request_counts', None),
                "created_at": getattr(batch, 'created_at', None),
                "expires_at": getattr(batch, 'expires_at', None),
                "completed_at": getattr(batch, 'completed_at', None),
                "archived_at": getattr(batch, 'archived_at', None)
            }
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in create_batch", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in create_batch", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def retrieve_batch(client: anthropic.Anthropic, batch_id: str) -> BatchRetrieveResponse:
    """Retrieve a specific batch"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        batch = client.messages.batches.retrieve(batch_id)

        return BatchRetrieveResponse(
            success=True,
            data={
                "id": batch.id,
                "type": batch.type,
                "processing_status": getattr(batch, 'processing_status', None),
                "request_counts": getattr(batch, 'request_counts', None),
                "created_at": getattr(batch, 'created_at', None),
                "expires_at": getattr(batch, 'expires_at', None),
                "completed_at": getattr(batch, 'completed_at', None),
                "archived_at": getattr(batch, 'archived_at', None)
            }
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in retrieve_batch", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in retrieve_batch", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def list_batches(client: anthropic.Anthropic, limit: int = 20) -> BatchListResponse:
    """List all batches"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        batches = client.messages.batches.list(limit=limit)

        batch_list = []
        for batch in batches.data:
            batch_list.append({
                "id": batch.id,
                "type": batch.type,
                "processing_status": getattr(batch, 'processing_status', None),
                "request_counts": getattr(batch, 'request_counts', None),
                "created_at": getattr(batch, 'created_at', None),
                "expires_at": getattr(batch, 'expires_at', None),
                "completed_at": getattr(batch, 'completed_at', None),
                "archived_at": getattr(batch, 'archived_at', None)
            })

        return BatchListResponse(
            success=True,
            data=batch_list
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in list_batches", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in list_batches", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def cancel_batch(client: anthropic.Anthropic, batch_id: str) -> BatchCancelResponse:
    """Cancel a batch"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        batch = client.messages.batches.cancel(batch_id)

        return BatchCancelResponse(
            success=True,
            data={
                "id": batch.id,
                "type": batch.type,
                "processing_status": getattr(batch, 'processing_status', None),
                "request_counts": getattr(batch, 'request_counts', None),
                "created_at": getattr(batch, 'created_at', None),
                "expires_at": getattr(batch, 'expires_at', None),
                "completed_at": getattr(batch, 'completed_at', None),
                "archived_at": getattr(batch, 'archived_at', None)
            }
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in cancel_batch", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in cancel_batch", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def delete_batch(client: anthropic.Anthropic, batch_id: str) -> BatchDeleteResponse:
    """Delete a batch"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        result = client.messages.batches.delete(batch_id)

        return BatchDeleteResponse(
            success=True,
            data={
                "id": result.id,
                "deleted": True
            }
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in delete_batch", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in delete_batch", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def get_batch_results(client: anthropic.Anthropic, batch_id: str):
    """Get batch results as a streaming response"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        results = client.messages.batches.results(batch_id)

        # This returns a JSONLDecoder that we need to stream
        # For now, we'll collect all results and return them
        # In a production environment, you'd want to stream these
        all_results = []
        for result in results:
            all_results.append({
                "custom_id": result.custom_id,
                "result": {
                    "type": result.result.type,
                    "message": {
                        "id": result.result.message.id,
                        "type": result.result.message.type,
                        "role": result.result.message.role,
                        "content": [content.model_dump() for content in result.result.message.content],
                        "model": result.result.message.model,
                        "stop_reason": result.result.message.stop_reason,
                        "stop_sequence": result.result.message.stop_sequence,
                        "usage": {
                            "input_tokens": getattr(result.result.message.usage, 'input_tokens', None),
                            "output_tokens": getattr(result.result.message.usage, 'output_tokens', None)
                        } if result.result.message.usage else None
                    } if hasattr(result.result, 'message') else None
                } if hasattr(result, 'result') else None
            })

        return BatchResultsResponse(
            success=True,
            data={"results": all_results}
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in get_batch_results", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in get_batch_results", error=str(e), batch_id=batch_id)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
