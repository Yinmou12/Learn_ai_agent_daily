# Agent Backend API

这是一个基于 FastAPI 的 Agent 后端服务骨架，用于练习后端项目结构、JWT 登录认证、SQLite 持久化、统一响应、统一异常处理、请求日志和基础测试。

## 功能

- FastAPI 路由模块化
- Pydantic 请求/响应校验
- JWT 登录认证
- SQLite 用户持久化
- 密码哈希存储
- 用户注册、登录、当前用户查询
- 用户分页查询
- 统一响应结构
- 统一异常处理
- 请求日志中间件
- TestClient 接口测试

## 环境准备

创建虚拟环境后安装依赖：

```powershell
python -m pip install -r requirements.txt
```

复制 `.env.example` 为 `.env`，并填写本地配置：

```
Copy-Item .env.example .env
```

## 启动服务

```
uvicorn app.main:app --reload
```

接口文档：

```
http://127.0.0.1:8000/docs
```

## 数据库

默认使用 SQLite：

```
DATABASE_URL=sqlite:///data/app.db
```

服务启动时会初始化数据库表。`data/app.db` 是本地数据库文件，不建议提交到 Git。

## 接口说明

健康检查：

```
GET /health
```

注册：

```
POST /api/v1/auth/register
```

登录：

```
POST /api/v1/auth/login
```

当前用户：

```
GET /api/v1/users/me
```

简历解析：

```
POST /api/v1/resumes/parse

请求头：
Authorization: Bearer <token>

请求体：
{
  "resume_text": "张三，Python 后端开发...",
  "use_fake": true
}
```

面试题库：

```
新增面试题：

POST /api/v1/questions
Authorization: Bearer <token>

{
  "question": "请解释 FastAPI 中 Depends 的作用。",
  "reference_answer": "Depends 用于声明依赖注入，让路由函数自动获取数据库连接、当前用户等对象。",
  "key_points": ["依赖注入", "复用公共逻辑", "常用于认证和数据库 Session"],
  "difficulty": "medium",
  "tags": ["FastAPI", "Depends", "后端分层"]
}
```

```
查询面试题：

GET /api/v1/quesrtions
Authorization: Bearer <token>

tag			按技能标签筛选
difficulty	可选，用于按难度筛选
```

用户分页：

```
GET /api/v1/users?page=1&page_size=10
```

聊天接口：

```
POST /api/v1/chat
```

需要登录的接口请携带请求头：

```
Authorization: Bearer <access_token>
```

## 运行测试

```
python -m unittest
```

## 本地检查

先启动服务：

```
uvicorn app.main:app --reload
```

再运行：

```
python scripts/smoke_check.py
```

## 项目结构

```
app/
├── api/routes/          # 路由层
├── services/            # 服务层
├── clients/             # 外部 API 客户端
├── models/              # SQLAlchemy 模型
├── db/                  # 数据库连接与 Session
├── dependencies/        # FastAPI 依赖注入
├── middlewares/         # 中间件
├── core/                # 日志等核心配置
├── security/            # JWT 与密码哈希
└── utils/               # 通用响应构造
```

## 分层说明

路由层负责接收 HTTP 请求，服务层负责业务流程，客户端层负责调用外部大模型 API，数据库层负责数据持久化。这样可以避免所有逻辑堆在 `main.py` 中，方便后续扩展简历解析、岗位匹配、RAG 出题和 AI 评分。

```
运行方式：

```powershell
cd D:\_Software_Projects\codex\ai_agent_daily_mentor\week2_agent_api
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
python scripts/smoke_check.py
```





```

```



