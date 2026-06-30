# Week2 Agent Backend API

这是 Week2 的最小 FastAPI 后端骨架，用于把 Week1 的 CLI 能力逐步迁移成 HTTP API。

## 安装依赖

进入项目路径

```powershell
conda create -n your_env_name python=X.X
```

不要使用3.12.5版本的Python，会导致VSCode中无法进行代码格式自动规整

```powershell
python -m pip install requirements.txt
```



## 项目结构

```text
week2_agent_api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   ├── exceptions.py
│   ├── clients/
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── chat_service.py
│   └── utils/
│       ├── __init__.py
│       └── response.py
├── .env
└── requirements.txt
```

### .env

```txt
LLM_API_KEY=你的 API Key
LLM_BASE_URL=https://你的大模型服务地址/v1
LLM_MODEL=你的模型名
```

### .requirements.txt

```text
python-dotenv
httpx
rich
fastapi
uvicorn
pydantic
```

## 项目分层说明

当前 FastAPI 后端采用三层结构：路由层、服务层、客户端层。

### 1. 路由层：`app/main.py`

路由层负责接收 HTTP 请求，并返回统一响应。

主要职责：

- 定义接口路径，例如 `/health`、`/api/v1/chat`
- 接收已经通过 Pydantic 校验的请求数据
- 调用服务层函数处理业务
- 将结果包装成统一响应格式
- 捕获可预期业务异常并返回错误信息

路由层不直接写大模型 API 请求，也不处理复杂业务逻辑。

### 2. 服务层：`app/services/chat_service.py`

服务层负责具体业务流程。

主要职责：

- 根据用户输入生成回答
- 决定调用真实大模型还是假回答
- 组织业务处理步骤
- 屏蔽路由层和底层客户端调用细节

服务层不关心 HTTP 路径、状态码和响应格式。

### 3. 客户端层：`app/clients/llm_client.py`

客户端层负责和外部服务通信。

主要职责：

- 构造大模型 API 请求地址
- 构造请求头和请求体
- 发送 HTTP 请求
- 处理超时、状态码错误、网络错误
- 解析大模型返回结果

客户端层不关心 FastAPI 路由，也不直接返回 API 响应结构。

## 当前调用链

```text
POST /api/v1/chat
-> app/main.py 的 chat()
-> app/services/chat_service.py 的 generate_llm_answer()
-> app/clients/llm_client.py 的 call_llm()
-> 外部大模型 API
```



## 运行方式

```powershell
cd D:\_Software_Projects\codex\ai_agent_daily_mentor
conda activate ai_agent_mentor
python -m pip install -r requirements.txt
cd week2_agent_api
uvicorn app.main:app --reload
```



### Day 8

--reload 表示开发模式下自动重载：修改代码后，服务会自动重启。

```text
uvicorn app.main:app --reload	
INFO:     Will watch for changes in these directories: ['D:...\\week2_agent_api']	uvicorn会监听显示目录下的文件变化
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)	服务已经运行在http://127.0.0.1:8000
INFO:     Started reloader process [22356] using StatReload		因为使用了--reload，所以uvicorn会额外启动一个重载进程
INFO:     Started server process [19600]	表示真正处理 HTTP 请求的服务进程启动了
INFO:     Waiting for application startup.	表示 FastAPI 正在执行启动流程。如果你代码里有启动事件，比如连接数据库、初始化资源，会在这里执行。
INFO:     Application startup complete.		表示应用启动完成，可以正常接收请求。
INFO:     127.0.0.1:2791 - "GET / HTTP/1.1" 404 Not Found	访问了根路径 '/' 目前没有定义接口 '/'
INFO:     127.0.0.1:2791 - "GET /favicon.ico HTTP/1.1" 404 Not Found	浏览器自动请求网站图标：/favicon.ico
INFO:     127.0.0.1:59478 - "GET / HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:59478 - "GET /favicon.ico HTTP/1.1" 404 Not Found 
INFO:     127.0.0.1:33247 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:12073 - "GET /openapi.json HTTP/1.1" 200 OK
```

**总结一下**

```text
服务启动成功：是
/docs 可访问：是
/ 返回 404：因为你没写根路由
/favicon.ico 返回 404：浏览器自动请求图标，可以忽略
```

你现在应该优先访问：

```text
http://127.0.0.1:8000/docs
```

而不是：

```text
http://127.0.0.1:8000/
```



### Day 9

