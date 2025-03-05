import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, openai
from app.core.config import settings

app = FastAPI(
    title="GitHub OAuth & OpenAI API Service",
    description="A FastAPI backend for GitHub OAuth authentication and OpenAI API forwarding",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth.router, prefix="/api")
app.include_router(openai.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "GitHub OAuth & OpenAI API Service"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )