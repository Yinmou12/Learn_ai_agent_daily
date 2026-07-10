# Project Structure

本文档说明 `week2_agent_api` 当前 FastAPI 后端项目的分层结构、各目录职责和一次请求的调用链路。

## 总体目标

当前项目不是单文件 Demo，而是一个最小可扩展的 Agent 后端骨架。核心设计目标是：

- 路由层只负责 HTTP 入口。
- 服务层只负责业务流程。
- 客户端层只负责外部 API 调用。
- 数据库层只负责数据持久化。
- 安全层只负责认证、JWT 和密码哈希。
- 中间件和异常处理负责通用横切逻辑。

这样做可以避免所有逻辑堆在 `main.py` 中，后续扩展简历解析、岗位匹配、RAG 出题和 AI 评分时，可以按模块增加代码。

## 当前目录结构

```text
week2_agent_api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── exceptions.py
│   ├── exception_handlers.py
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── chat.py
│   │       ├── debug.py
│   │       ├── health.py
│   │       ├── users.py
│   │       └── version.py
│   ├── clients/
│   │   └── llm_client.py
│   ├── core/
│   │   ├── logging_config.py
│   │   └── request_context.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── dependencies/
│   │   └── auth.py
│   ├── middlewares/
│   │   └── request_log.py
│   ├── models/
│   │   └── user.py
│   ├── security/
│   │   ├── jwt.py
│   │   └── password.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   └── user_service.py
│   └── utils/
│       └── response.py
├── tests/
├── docs/
├── .env
├── .env.example
└── README.md
```

## `app/main.py`：应用装配入口

`main.py` 是 FastAPI 应用的总装配入口。

主要职责：

- 创建 `FastAPI` 应用对象。
- 初始化数据库表。
- 注册中间件。
- 注册全局异常处理器。
- 注册各个 router。

`main.py` 不应该直接写业务逻辑、数据库查询或大模型请求。

典型职责示例：

```python
app.add_middleware(RequestLogMiddleware)
app.add_exception_handler(AuthError, auth_error_handler)
app.include_router(users_router)
```

## `app/api/routes/`：路由层

路由层负责定义 HTTP 接口。

当前路由模块：

| 文件 | 职责 |
|---|---|
| `auth.py` | 注册、登录等认证接口 |
| `users.py` | 当前用户、用户列表、用户信息更新 |
| `chat.py` | 聊天接口 |
| `health.py` | 健康检查 |
| `version.py` | 服务版本查询 |
| `debug.py` | 本地调试接口 |

路由层应该只做：

- 接收请求参数。
- 调用服务层函数。
- 返回统一响应结构。
- 通过 `Depends` 声明认证、数据库 Session 等依赖。

路由层不应该直接：

- 写 SQLAlchemy 查询。
- 调用 `httpx.post()`。
- 处理密码哈希。
- 读取 `.env`。

## `app/services/`：服务层

服务层负责业务流程。

当前服务模块：

| 文件 | 职责 |
|---|---|
| `auth_service.py` | 认证相关业务 |
| `user_service.py` | 用户注册、查询、更新、分页 |
| `chat_service.py` | 聊天业务，决定使用假回答还是真实 LLM |

服务层负责把多个底层能力组织成一个业务动作。

例如用户注册流程：

```text
接收 UserCreate
-> 检查用户名是否已存在
-> 哈希密码
-> 创建 User ORM 对象
-> 写入数据库
-> 返回 UserProfile 或 UserPublic
```

服务层可以调用：

- 数据库模型。
- 安全工具。
- 客户端层。
- 异常类。

服务层不应该关心：

- HTTP 路径。
- HTTP 状态码。
- FastAPI router。

## `app/clients/`：客户端层

客户端层负责和外部服务通信。

当前主要文件：

```text
app/clients/llm_client.py
```

它负责：

- 构造大模型 API 请求 URL。
- 构造请求头和请求体。
- 调用外部大模型接口。
- 处理超时、状态码错误、网络错误。
- 解析 OpenAI-compatible 响应结构。

客户端层不应该知道：

- 这个调用来自哪个路由。
- HTTP 接口最终怎么返回。
- 当前用户是谁。

## `app/models/`：数据库模型层

模型层定义数据库表结构。

当前模型：

```text
app/models/user.py
```

`User` 类对应数据库中的 `users` 表。

关系可以这样理解：

```text
Model 是 Python 类。
Table 是数据库里的真实表。
Session 是 Python 操作数据库的通道。
```

例如：

```python
class User(Base):
    __tablename__ = "users"
```

这里 `User` 是 SQLAlchemy Model，`users` 是数据库表名。

## `app/db/`：数据库连接与 Session

数据库层负责创建数据库连接和提供 Session。

当前文件：

| 文件 | 职责 |
|---|---|
| `base.py` | 定义所有 ORM Model 的基类 |
| `session.py` | 创建 engine、SessionLocal、get_db、init_db |

`get_db()` 通常会被 FastAPI 的 `Depends` 使用：

```python
db: Session = Depends(get_db)
```

它的作用是为每个请求创建一个数据库 Session，并在请求结束后关闭。

## `app/schemas.py`：Pydantic 数据模型

`schemas.py` 定义请求和响应的数据结构。

主要包括：

- 请求体模型，例如 `LoginRequest`、`UserCreate`、`ChatRequest`。
- 响应数据模型，例如 `TokenData`、`UserProfile`、`UserPublic`、`UserListData`。
- 统一响应模型，例如 `ApiResponse`、`ErrorDetail`。

需要注意：

- `schemas.py` 不直接访问数据库。
- `schemas.py` 不写业务逻辑。
- 对外返回用户信息时，不应该包含 `password_hash`。

## `app/security/`：安全层

安全层负责认证相关的底层能力。

当前文件：

| 文件 | 职责 |
|---|---|
| `jwt.py` | 创建和解析 JWT token |
| `password.py` | 密码哈希与密码校验 |

安全层不应该直接处理 HTTP 路由，也不应该直接操作响应结构。

## `app/dependencies/`：依赖注入

该目录存放 FastAPI 依赖函数。

当前主要文件：

```text
app/dependencies/auth.py
```

它负责：

- 从请求头读取 `Authorization: Bearer <token>`。
- 解析 JWT。
- 查询当前用户。
- 给受保护接口提供 `current_user`。

典型用法：

```python
current_user: UserProfile = Depends(get_current_user)
```

## `app/middlewares/`：中间件

中间件负责所有请求都会经过的通用逻辑。

当前文件：

```text
app/middlewares/request_log.py
```

请求日志中间件负责：

- 生成 `request_id`。
- 记录请求方法。
- 记录请求路径。
- 记录响应状态码。
- 记录请求耗时。
- 错误时记录异常日志。

中间件只记录日志，不负责替代异常处理器。

## `app/core/`：核心配置

当前文件：

| 文件 | 职责 |
|---|---|
| `logging_config.py` | 配置日志格式、日志级别、输出方式 |
| `request_context.py` | 保存当前请求的 `request_id` |

`request_context.py` 使用 `ContextVar` 保存请求级上下文，使统一响应和日志可以拿到同一个 `request_id`。

## `app/utils/`：通用工具

当前文件：

```text
app/utils/response.py
```

它负责构造统一响应：

```python
make_success_response(...)
make_error_response(...)
```

这样路由层不需要手动拼接：

```json
{
  "success": true,
  "data": {},
  "error": null,
  "request_id": "..."
}
```

## `app/exceptions.py` 与 `app/exception_handlers.py`

异常相关逻辑拆成两层：

| 文件 | 职责 |
|---|---|
| `exceptions.py` | 定义异常类型 |
| `exception_handlers.py` | 定义异常如何转成 HTTP 响应 |

例如：

```text
AuthError -> 401
NotFoundError -> 404
ParameterError -> 422
AppError -> 400
```

这样服务层只需要：

```python
raise NotFoundError("用户不存在")
```

不用关心最终 HTTP 状态码和响应格式。

## 一次用户列表请求的调用链

```text
GET /api/v1/users?page=1&page_size=10
-> RequestLogMiddleware 生成 request_id 并记录请求
-> users.py 中的 get_users()
-> Depends(get_current_user) 校验 JWT
-> Depends(get_db) 创建数据库 Session
-> user_service.py 中的 list_users()
-> SQLAlchemy 查询 users 表
-> response.py 构造统一成功响应
-> RequestLogMiddleware 记录状态码和耗时
-> 返回 JSON 响应
```

## 一次聊天请求的调用链

```text
POST /api/v1/chat
-> RequestLogMiddleware
-> chat.py 中的 chat()
-> Depends(get_current_user) 校验 JWT
-> chat_service.py 中的 generate_chat_answer()
-> 如果 use_fake=True，返回假回答
-> 如果 use_fake=False，调用 llm_client.py
-> response.py 构造统一响应
-> 返回 JSON 响应
```

## 分层带来的好处

### 1. 便于维护

接口多了以后，不会把所有代码堆进 `main.py`。

### 2. 便于测试

可以分别测试：

- 路由层是否返回正确响应。
- 服务层是否处理业务规则。
- 客户端层是否正确解析大模型响应。
- 数据库层是否正确读写数据。

### 3. 便于扩展

后续新增简历解析时，可以新增：

```text
app/api/routes/resumes.py
app/services/resume_service.py
app/models/resume.py
```

不需要改乱已有用户、认证和聊天模块。

### 4. 便于排查问题

请求日志、`request_id`、统一异常响应可以让问题排查链路更清晰：

```text
用户反馈 request_id
-> 查请求日志
-> 查错误日志
-> 定位具体路由和服务层函数
```

## 新增功能时的推荐流程

以后新增一个功能，建议按这个顺序：

1. 在 `schemas.py` 定义请求和响应模型。
2. 如需数据库，先在 `models/` 定义 ORM Model。
3. 在 `services/` 编写业务逻辑。
4. 在 `api/routes/` 新增路由文件。
5. 在 `main.py` 注册 router。
6. 在 `tests/` 增加接口测试或服务层测试。
7. 在 README 或 `docs/` 中补充接口说明。

## 当前项目和 AI-Interview 的关系

当前项目是后续 `AI-Interview` 的后端雏形。

现在已有能力：

- 用户认证。
- 用户信息持久化。
- 受保护接口。
- LLM 客户端封装。
- 统一响应。
- 统一异常处理。
- 请求日志。
- 基础测试。

后续可以在这个骨架上继续加入：

- 简历解析模块。
- 岗位匹配模块。
- 面试题生成模块。
- RAG 检索模块。
- AI 评分模块。
- 面试报告模块。
