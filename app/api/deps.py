from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any, Optional

from app.core.security import verify_token

# 定义OAuth2密码流，指定令牌URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/github/callback")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    获取当前用户，用于依赖注入
    """
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从JWT令牌中提取用户信息
    user_data = {
        "github_id": payload.get("github_id"),
        "username": payload.get("username"),
        "name": payload.get("name"),
        "email": payload.get("email"),
        "avatar_url": payload.get("avatar_url"),
    }
    
    if not user_data["github_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_data