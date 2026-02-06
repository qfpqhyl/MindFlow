# MindFlow Backend

基于 FastAPI 的 MindFlow 后端服务，提供聊天、文档管理和定时任务功能。

## 功能特性

- ✅ JWT 用户认证
- ✅ 对话管理（创建、查询、更新、删除）
- ✅ 消息管理（发送、接收，支持流式响应）
- ✅ NVIDIA AI 集成（Llama 3.1 等模型）
- ✅ 文档管理（完整 CRUD 操作）
- ✅ 智能整理（对话转文档 + AI 摘要）
- ✅ 定时任务管理
- ✅ 邮件提醒（飞书 SMTP）
- ✅ 定时任务调度器
- ✅ 标签系统
- ✅ 全文搜索

## 技术栈

- **框架**: FastAPI 0.115.0
- **数据库**: SQLite 3
- **AI 服务**: NVIDIA API (Llama 3.1)
- **邮件服务**: 飞书 SMTP (aiosmtplib)
- **任务调度**: APScheduler
- **认证**: JWT (python-jose)
- **密码加密**: Passlib + bcrypt

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

```env
# NVIDIA API - 必需
NVIDIA_API_KEY=your-nvidia-api-key

# 邮件配置 - 可选（如需使用邮件提醒）
SMTP_USERNAME=your-email@feishu.cn
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=your-email@feishu.cn

# JWT 密钥 - 生产环境请修改
SECRET_KEY=your-secret-key-change-this-in-production
```

### 4. 启动服务

**方式一：使用启动脚本**

```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

**方式二：手动启动**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问 API

- API 服务: http://localhost:8000
- 交互式文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库模型
│   ├── auth.py                # 认证工具（JWT、密码加密）
│   ├── dependencies.py        # FastAPI 依赖
│   ├── email_service.py       # 邮件服务
│   ├── ai_service.py          # NVIDIA AI 服务
│   ├── scheduler.py           # 任务调度器
│   ├── schemas.py             # Pydantic 数据模型
│   └── api/                   # API 路由
│       ├── __init__.py
│       ├── auth.py            # 认证接口
│       ├── conversations.py   # 对话管理
│       ├── messages.py        # 消息管理
│       ├── organize.py        # 整理功能
│       ├── documents.py       # 文档管理
│       ├── tasks.py           # 任务管理
│       ├── users.py           # 用户管理
│       ├── emails.py          # 邮件通知
│       └── ai.py              # AI 配置
├── main.py                    # 应用入口
├── requirements.txt           # 依赖列表
├── .env.example              # 环境变量示例
├── start.sh                  # 启动脚本（macOS/Linux）
├── start.bat                 # 启动脚本（Windows）
└── test_api.py               # API 测试脚本
```

## API 端点

### 认证模块
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新令牌

### 对话管理
- `GET /api/v1/conversations` - 获取对话列表
- `POST /api/v1/conversations` - 创建对话
- `GET /api/v1/conversations/{id}` - 获取对话详情
- `PUT /api/v1/conversations/{id}` - 更新对话标题
- `DELETE /api/v1/conversations/{id}` - 删除对话

### 消息管理
- `GET /api/v1/conversations/{id}/messages` - 获取消息列表
- `POST /api/v1/conversations/{id}/messages` - 发送消息
- `DELETE /api/v1/messages/{id}` - 删除消息

### 整理功能
- `POST /api/v1/organize/to-document` - 整理对话为文档
- `POST /api/v1/organize/suggestions` - 获取整理建议

### 文档管理
- `GET /api/v1/documents` - 获取文档列表
- `GET /api/v1/documents/{id}` - 获取文档详情
- `POST /api/v1/documents` - 创建文档
- `PUT /api/v1/documents/{id}` - 更新文档
- `DELETE /api/v1/documents/{id}` - 删除文档
- `GET /api/v1/documents/search` - 搜索文档

### 任务管理
- `GET /api/v1/tasks` - 获取任务列表
- `GET /api/v1/tasks/{id}` - 获取任务详情
- `POST /api/v1/tasks` - 创建任务
- `PUT /api/v1/tasks/{id}` - 更新任务
- `POST /api/v1/tasks/{id}/complete` - 完成任务
- `DELETE /api/v1/tasks/{id}` - 删除任务
- `POST /api/v1/tasks/{id}/send-reminder` - 发送提醒邮件

### 用户管理
- `GET /api/v1/users/me` - 获取用户信息
- `PUT /api/v1/users/me` - 更新用户信息
- `POST /api/v1/users/change-password` - 修改密码
- `PUT /api/v1/users/email-settings` - 更新邮件设置

### AI 配置
- `GET /api/v1/ai/models` - 获取可用模型列表
- `PUT /api/v1/ai/models/default` - 设置默认模型

## 测试

运行 API 测试脚本：

```bash
python test_api.py
```

测试脚本会自动执行以下操作：
1. 健康检查
2. 用户注册/登录
3. 创建对话
4. 发送消息
5. 创建文档
6. 创建任务

## 数据库

数据库文件位置：`./data/mindflow.db`

首次启动时会自动创建以下表：
- `users` - 用户表
- `conversations` - 对话表
- `messages` - 消息表
- `documents` - 文档表
- `document_tags` - 文档标签表
- `tasks` - 任务表
- `email_notifications` - 邮件通知表
- `user_settings` - 用户设置表

## 定时任务调度

后台任务调度器每 5 分钟自动检查一次到期任务并发送邮件提醒。

## NVIDIA API 配置

1. 访问 [NVIDIA API Catalog](https://build.nvidia.com/)
2. 创建账户并获取 API Key
3. 在 `.env` 文件中配置 `NVIDIA_API_KEY`

支持的模型：
- meta/llama-3.1-405b-instruct
- meta/llama-3.1-70b-instruct
- meta/llama-3.1-8b-instruct
- mistralai/mistral-large
- google/gemma-2-27b-it

## 邮件配置（飞书 SMTP）

如需使用邮件提醒功能，配置以下参数：

```env
SMTP_HOST=smtp.feishu.cn
SMTP_PORT=465
SMTP_USERNAME=your-email@feishu.cn
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=your-email@feishu.cn
EMAIL_USE_TLS=true
```

获取 SMTP 密码：
1. 登录飞书邮箱
2. 设置 -> SMTP 设置
3. 生成 SMTP 密码

## 安全注意事项

### 生产环境部署前必须修改：

1. **JWT 密钥**
   ```env
   SECRET_KEY=使用强随机字符串
   ```

2. **CORS 配置**
   ```env
   CORS_ORIGINS=["https://your-domain.com"]
   ```

3. **数据库安全**
   - 设置适当的文件权限
   - 定期备份数据库

4. **API 密钥保护**
   - 不要在代码中硬编码 API 密钥
   - 使用环境变量
   - 定期轮换密钥

## 开发

### 添加新的 API 端点

1. 在 `app/schemas.py` 中定义数据模型
2. 在 `app/api/` 中创建或修改路由文件
3. 在 `main.py` 中注册路由

### 运行开发服务器

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 故障排除

### 问题：无法启动服务

**解决方案**：
1. 检查 Python 版本是否 >= 3.8
2. 确保虚拟环境已激活
3. 重新安装依赖：`pip install -r requirements.txt`

### 问题：API 返回 401 错误

**解决方案**：
1. 检查 JWT token 是否有效
2. 确认 `SECRET_KEY` 配置正确
3. 尝试重新登录获取新 token

### 问题：AI 消息无响应

**解决方案**：
1. 检查 `NVIDIA_API_KEY` 是否正确
2. 确认网络可以访问 NVIDIA API
3. 查看 API 配额是否用尽

### 问题：邮件发送失败

**解决方案**：
1. 确认 SMTP 配置正确
2. 检查飞书邮箱是否开启 SMTP 服务
3. 验证 SMTP 密码是否正确

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue。
