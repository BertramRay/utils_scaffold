from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
import httpx
from typing import Dict, Any, AsyncGenerator

from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter(prefix="/openai", tags=["openai"])


async def stream_openai_response(request_data: Dict[str, Any], openai_api_key: str) -> AsyncGenerator[bytes, None]:
    """
    流式转发OpenAI API响应
    """
    url = f"{settings.OPENAI_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }
    
    # 确保请求中包含stream=True
    request_data["stream"] = True
    
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", url, json=request_data, headers=headers, timeout=60.0
        ) as response:
            if response.status_code != 200:
                error_detail = await response.text()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {error_detail}"
                )
            
            async for chunk in response.aiter_bytes():
                yield chunk


@router.post("/chat/completions")
async def openai_chat_completions(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    转发请求到OpenAI的chat/completions API，支持流式响应
    """
    request_data = await request.json()
    
    # 使用应用配置中的API密钥，或者允许客户端提供自己的密钥
    openai_api_key = settings.OPENAI_API_KEY
    
    # 如果请求中包含API密钥，使用请求中的密钥（可选功能）
    client_api_key = request.headers.get("X-OpenAI-Api-Key")
    if client_api_key:
        openai_api_key = client_api_key
    
    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key is required"
        )
    
    # 检查是否请求流式响应
    is_stream = request_data.get("stream", False)
    
    if is_stream:
        return StreamingResponse(
            stream_openai_response(request_data, openai_api_key),
            media_type="text/event-stream"
        )
    else:
        # 对于非流式请求，直接转发并返回完整响应
        url = f"{settings.OPENAI_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=request_data, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API error: {response.text}"
                )
            
            return response.json()