"""
Models API endpoints for Anthropic SDK
"""

from fastapi import HTTPException
import anthropic
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

class ModelInfoResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ModelsListResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

def get_model_info(client: anthropic.Anthropic, model_id: str) -> ModelInfoResponse:
    """Get information about a specific model - returns static info as Anthropic doesn't support model retrieval"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        # Static model information since Anthropic doesn't support model retrieval
        model_info_map = {
            "claude-3-5-sonnet-20241022": {
                "id": "claude-3-5-sonnet-20241022",
                "type": "text",
                "display_name": "Claude 3.5 Sonnet",
                "created_at": "2024-10-22T00:00:00Z"
            },
            "claude-3-5-haiku-20241022": {
                "id": "claude-3-5-haiku-20241022", 
                "type": "text",
                "display_name": "Claude 3.5 Haiku",
                "created_at": "2024-10-22T00:00:00Z"
            },
            "claude-3-opus-20240229": {
                "id": "claude-3-opus-20240229",
                "type": "text",
                "display_name": "Claude 3 Opus",
                "created_at": "2024-02-29T00:00:00Z"
            },
            "claude-3-sonnet-20240229": {
                "id": "claude-3-sonnet-20240229",
                "type": "text",
                "display_name": "Claude 3 Sonnet",
                "created_at": "2024-02-29T00:00:00Z"
            },
            "claude-3-haiku-20240307": {
                "id": "claude-3-haiku-20240307",
                "type": "text",
                "display_name": "Claude 3 Haiku", 
                "created_at": "2024-03-07T00:00:00Z"
            }
        }

        if model_id not in model_info_map:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")

        return ModelInfoResponse(
            success=True,
            data=model_info_map[model_id]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in get_model_info", error=str(e), model_id=model_id)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def list_models(client: anthropic.Anthropic) -> ModelsListResponse:
    """List all available models - returns static list as Anthropic doesn't support model listing"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        # Anthropic doesn't currently support model listing via API
        # Return the known available models as of 2024
        static_models = [
            {
                "id": "claude-3-5-sonnet-20241022",
                "type": "text",
                "display_name": "Claude 3.5 Sonnet",
                "created_at": "2024-10-22T00:00:00Z"
            },
            {
                "id": "claude-3-5-haiku-20241022",
                "type": "text", 
                "display_name": "Claude 3.5 Haiku",
                "created_at": "2024-10-22T00:00:00Z"
            },
            {
                "id": "claude-3-opus-20240229",
                "type": "text",
                "display_name": "Claude 3 Opus",
                "created_at": "2024-02-29T00:00:00Z"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "type": "text",
                "display_name": "Claude 3 Sonnet", 
                "created_at": "2024-02-29T00:00:00Z"
            },
            {
                "id": "claude-3-haiku-20240307",
                "type": "text",
                "display_name": "Claude 3 Haiku",
                "created_at": "2024-03-07T00:00:00Z"
            }
        ]

        return ModelsListResponse(
            success=True,
            data=static_models
        )

    except Exception as e:
        logger.error("Unexpected error in list_models", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
