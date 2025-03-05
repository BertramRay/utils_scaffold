from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from datetime import timedelta
from typing import Dict, Any, Optional

from app.core.config import settings
from app.core.security import create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/github/login")
async def github_login():
    """
    生成GitHub OAuth登录URL并重定向用户
    """
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "read:user",
        "state": "random_state",  # 在生产环境中应该使用安全的随机值
    }
    
    auth_url = f"{settings.GITHUB_AUTH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(code: str, state: Optional[str] = None):
    """
    处理GitHub OAuth回调，获取访问令牌并创建JWT
    """
    # 验证state参数（在生产环境中应该验证）
    
    # 交换code获取GitHub访问令牌
    token_params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
    }
    
    headers = {"Accept": "application/json"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.GITHUB_TOKEN_URL,
            data=token_params,
            headers=headers
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get GitHub access token"
            )
        
        token_data = response.json()
        github_token = token_data.get("access_token")
        
        if not github_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub access token not found in response"
            )
        
        # 获取用户信息
        user_response = await client.get(
            f"{settings.GITHUB_API_URL}/user",
            headers={"Authorization": f"token {github_token}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get GitHub user info"
            )
        
        user_data = user_response.json()
        
        # 创建JWT令牌
        user_info = {
            "github_id": user_data.get("id"),
            "username": user_data.get("login"),
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "avatar_url": user_data.get("avatar_url"),
        }
        
        access_token = create_access_token(subject=user_info)
        
        return JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_info
        })


@router.get("/me", response_model=Dict[str, Any])
async def read_users_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return current_user