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

```
week2_agent_api/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py				# 登录接口和当前用户接口
│   │       ├── health.py           # 健康检查接口
│   │       ├── version.py          # 版本查询接口
│   │       ├── chat.py             # 聊天接口
│   │       └── debug.py            # 调试接口，可选
│   ├── clients/
│   │   ├── __init__.py
│   │   └── llm_client.py           # 外部大模型 API 调用封装
│   ├── dependencies
│   │   ├── __init__.py
│   │   ├── auth.py					# 从请求头中取 token，并得到当前用户
│   ├── security/
│   │   ├── __init__.py
│   │   ├── jwt.py					# 创建和解析 token
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_serivice.py		# 验证用户名密码
│   │   └── chat_service.py         # 聊天业务逻辑
│   │   └── password.py				# 明文密码改为哈希密码
│   └── utils/
│       ├── __init__.py
│       └── response.py             # 统一响应构造函数
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py			# 测试登录接口
│       ├── test_chat_mock.py
│       ├── test_route.py
│   ├── __init__.py
│   ├── config.py                  	# 环境变量读取与配置对象
│   ├── exception_handlers.py      	# 全局异常处理器
│   ├── exceptions.py              	# 自定义业务异常
│   ├── main.py                   	# FastAPI 应用创建、路由注册、异常处理注册
│   ├── schemas.py                 	# Pydantic 请求/响应模型
├── .env                            # 本地环境变量，不提交 Git
├── .env.example					# 环境变量示例，可提交 Git
├── requirements.txt                # 项目依赖
└── README.md                       # 项目说明、启动方式、接口说明
```

```text
main.py 是总装配入口
api/routes 是接口入口
services 是业务处理
clients 是外部服务调用
utils 是通用工具
```



```
这个后端项目我按职责拆成了路由层、服务层和客户端层。

路由层主要放在 `app/api/routes/` 中，负责定义 HTTP 接口，例如健康检查、版本查询和聊天接口。它只处理请求入口、参数接收和统一响应返回，不直接写复杂业务逻辑。

服务层放在 `app/services/` 中，负责具体业务流程。例如聊天接口会先进入路由函数，再由路由函数调用 `chat_service.py`，由服务层决定使用假回答还是真实大模型回答。

客户端层放在 `app/clients/` 中，负责和外部服务通信。例如 `llm_client.py` 专门封装大模型 API 调用，包括构造请求、发送 HTTP 请求、处理超时和状态码错误、解析模型响应。

这样拆分的好处是职责清晰：路由层不关心大模型请求细节，服务层不关心 HTTP 路径，客户端层不关心业务接口怎么返回。后续如果要扩展简历解析、岗位匹配、面试题生成，只需要新增对应的 service 和 route，不需要把所有逻辑堆在 `main.py` 里。
```



## 数据库说明

本项目当前使用 SQLite 作为本地开发数据库。

数据库连接地址配置在 `.env` 中：

```text
DATABASE_URL=sqlite:///data/app.db
```

启动 FastAPI 应用时，程序会调用 `init_db()` 自动创建数据库表：

```
Base.metadata.create_all(bind=engine)
```

如果本地没有数据库文件，启动后会自动生成：

```
data/app.db
```

### SQLite 文件位置

默认数据库文件路径：

```
week2_agent_api/data/app.db
```

`data/app.db` 是本地运行数据，不建议提交到 Git。

建议在 `.gitignore` 中加入：

```
data/app.db
*.db
```

如果需要重置本地数据，可以停止服务后删除：

```
Remove-Item data\app.db
```

然后重新启动服务：

```
uvicorn app.main:app --reload
```

程序会重新创建空数据库和数据表。





### .env

```txt
LLM_API_KEY=你的 API Key
LLM_BASE_URL=https://你的大模型服务地址/v1
LLM_MODEL=你的模型名
```

## 运行方式

```powershell
cd D:\_Software_Projects\codex\ai_agent_daily_mentor
conda activate ai_agent_mentor
python -m pip install -r requirements.txt
cd week2_agent_api
uvicorn app.main:app --reload
```



