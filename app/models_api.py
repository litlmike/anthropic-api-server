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
    """Get information about a specific model"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        model = client.models.retrieve(model_id)

        return ModelInfoResponse(
            success=True,
            data={
                "id": model.id,
                "type": model.type,
                "display_name": getattr(model, 'display_name', None),
                "created_at": getattr(model, 'created_at', None)
            }
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in get_model_info", error=str(e), model_id=model_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in get_model_info", error=str(e), model_id=model_id)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def list_models(client: anthropic.Anthropic) -> ModelsListResponse:
    """List all available models"""
    try:
        if not client:
            raise HTTPException(status_code=500, detail="Anthropic client not initialized")

        models = client.models.list()

        model_list = []
        for model in models.data:
            model_list.append({
                "id": model.id,
                "type": model.type,
                "display_name": getattr(model, 'display_name', None),
                "created_at": getattr(model, 'created_at', None)
            })

        return ModelsListResponse(
            success=True,
            data=model_list
        )

    except anthropic.APIError as e:
        logger.error("Anthropic API error in list_models", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in list_models", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
