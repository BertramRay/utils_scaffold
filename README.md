# GitHub OAuth & OpenAI API Service

这是一个基于 FastAPI 的后端 API 应用，用于支持 VS Code 扩展插件的 GitHub 登录和鉴权操作，并提供基于 JWT 的鉴权机制和 OpenAI 流式 API 转发服务。

## 功能特点

1. **GitHub 登录鉴权**
   - 实现 OAuth 2.0 流程支持 GitHub 登录
   - 提供 API 端点用于 GitHub 账户登录
   - 登录成功后生成 JWT 令牌用于后续鉴权

2. **JWT 鉴权**
   - 基于 JWT 的鉴权机制保护 API 端点
   - JWT 令牌包含用户基本信息并设置合理过期时间

3. **OpenAI 流式 API 转发**
   - 提供 API 端点接收请求并转发到 OpenAI API
   - 支持流式响应，实时返回 OpenAI 数据
   - 确保数据传输安全性

## 安装步骤

1. 克隆仓库

```bash
git clone <repository-url>
cd utils_scaffold
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量

复制 `.env.example` 文件为 `.env` 并填写相关配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填写 GitHub OAuth 应用的 Client ID 和 Client Secret 等信息
```

4. 运行应用

```bash
python main.py
```

应用将在 http://localhost:8000 上运行。

## API 端点

### GitHub 认证

- `GET /api/auth/github/login` - 重定向到 GitHub 登录页面
- `GET /api/auth/github/callback` - GitHub OAuth 回调，返回 JWT 令牌
- `GET /api/auth/me` - 获取当前登录用户信息（需要认证）

### OpenAI API 转发

- `POST /api/openai/chat/completions` - 转发请求到 OpenAI 的 chat/completions API
- `POST /api/openai/completions` - 转发请求到 OpenAI 的 completions API

## 使用方法

### 1. GitHub 登录

将用户重定向到 `/api/auth/github/login` 端点，用户完成 GitHub 登录后将被重定向回应用，并获得 JWT 令牌。

### 2. 使用 JWT 令牌访问受保护资源

在请求头中添加 `Authorization: Bearer <token>` 来访问受保护的 API 端点。

### 3. 使用 OpenAI API 转发

向 `/api/openai/chat/completions` 发送 POST 请求，请求体与 OpenAI API 格式相同，支持流式响应。

## 安全注意事项

- 在生产环境中，应该使用安全的随机值作为 JWT 密钥
- 限制 CORS 来源为特定域名
- 安全存储 GitHub OAuth 应用的 Client ID 和 Client Secret
- 避免在请求转发过程中泄露 OpenAI API 密钥