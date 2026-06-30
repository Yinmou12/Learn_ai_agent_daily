

# Week1

## 项目结构

```
weeik1_llm_cli/
├── app/
│   ├── __init__.py
│   ├── async_llm_client.py  职责只做异步大模型调用
│   ├── exceptions.py
│   ├── config.py  负责配置
│   ├── history.py  负责保存对话信息
│   ├── http_client.py  负责通用HTTP
│   ├── llm_client.py  负责大模型业务调用
├── data/
│   ├── history.json  对话信息存储
├── .venv  配置
├── .venv.example
├── async_demo.py
├── demo_get_params.py
├── main.py  负责流程
├── test_cli.py
├── test_config.py
├── test_env.py
├── test_history.py
├── test_http_client.py
├── test_llm_client.py
```



## Day2

理解 HTTP 请求最小结构。请求的结构：`method -> url -> headers -> body -> response status -> response json`

在使用 `httpx` 与大模型 API 交互时，实际上是在构建和解析一个标准化的 HTTP 报文。以下是这 6 个核心组件背后的真实技术原理：

**1.Request**

发送请求的过程，本质上是按协议规范组装一段文本或二进制流发送给目标服务器。

**Method（请求方法：定义动作的语义）**：HTTP 协议定义了多种方法（如 GET、POST、PUT、DELETE），用来告诉服务器你想执行什么**性质**的操作。

​	为什么请求 LLM 必须用 `POST`？：`GET` 方法通常用于“获取”静态数据，且它的参数只能拼接在 URL 后面（长度有限制，且不安全）。而调用大模型时，我们需要向服务器提交（POST）大量的参数（如长篇的 prompt、上下文历史等），这些庞大的数据必须放在不可见的 Body 中传输，只有 `POST` 方法符合这种语义和技术要求。



**URL（统一资源定位符：精准寻址）**：URL 不是一个简单的网址，它是一组严格的路由指令。以 `https://api.openai.com/v1/chat/completions` 为例，它被服务器拆解为：

- **协议 (`https://`)**：强制要求建立 TLS 加密隧道，保证你发给大模型的数据不被网络中间人窃听。
- **域名 (`api.openai.com`)**：通过 DNS 解析为具体的服务器 IP 地址。
- **路径 (`/v1/chat/completions`)**：这是 API 的**路由端点（Endpoint）**。`/v1` 代表接口版本号；`/chat/completions` 告诉服务器内部的网关：“把这个请求交给处理对话生成的那个微服务”。



**Headers（请求头：控制信息与元数据）**：Headers 是一系列键值对（Key-Value），它不包含你的业务数据（Prompt），但它控制着**通信的环境与权限**。调用 LLM 时，有两个 Header 是很重要的：

- **`Authorization: Bearer <你的API_KEY>`**： 身份鉴权字段。`Bearer` 是一种基于 Token 的认证机制，它的潜台词是“持有这个令牌的人即为合法用户”。服务器网关会首先拦截并校验这个 Key，如果无效，请求根本进不了大模型的计算集群。
- **`Content-Type: application/json`**： 内容协商字段。你通过这行代码告诉服务器的解析器：“我接下来的 Body 里装的是 JSON 格式的字符串，请按照 JSON 的语法规则进行反序列化”。如果不传这个头，服务器可能会把你的数据当成纯文本或乱码直接丢弃。



**Body（请求体：真正的业务负载 / Payload）**：这是请求的绝对核心，包含你要大模型执行的具体任务。现代 Web API 绝大多数使用 JSON（JavaScript Object Notation）格式。

在 Python 代码中，传给 `httpx.post(..., json={...})` 的字典，会在底层被自动转换为符合 JSON 规范的字符串，放入 HTTP 的 Body 区域。



**2.Response（服务器返回的响应）**

服务器计算完毕后，会按同样的结构把数据塞进网络连接退回来。

**Response Status（状态码：通信状态的机器协议）**：状态码是 HTTP 协议提供的一种高效机制，让客户端（你的代码）不需要去解析复杂的 Body 就能第一秒知道请求是成功还是失败。 它遵循严格的区间定义：

- **`2xx` (如 200 OK)**：请求完全成功，服务器不仅接受了，而且正常处理了。
- **`4xx` (客户端错误)**：**问题出在你的代码里。**
  - `400 Bad Request`：你发的 JSON 格式错了，或者少传了必填参数（如没写 `model`）。
  - `401 Unauthorized`：你的 API Key 错了或没传。
  - `404 Not Found`：你的 URL 路径拼写错了。
- **`5xx` (服务端错误)**：**问题出在服务器端，你的代码没毛病。**
  - `500 Internal Server Error` / `503 Service Unavailable`：大模型服务器宕机、或者并发量太大崩溃了。这种错误通常需要你的代码实现“重试机制（Retry）”。



**Response JSON（响应体：处理结果）**：当状态码为 200 时，这里面装的就是大模型的回答。 它同样是一个复杂的 JSON 结构。除了我们最关心的文本内容（通常位于深层路径 `choices[0].message.content`），它通常还会返回：

- **`id`**：这次请求的全局唯一追踪号（用于排查 bug）。
- **`usage`**：记录这次请求消耗了多少 `prompt_tokens` 和 `completion_tokens`，这是 API 扣费的依据。



### 问题

**1.`headers` 和 `json body` 的区别**

`headers` 是 HTTP 请求的“元信息”，用来告诉服务端：这次请求是谁发的、数据格式是什么、是否有认证信息。例如：

```
headers = {
    "Authorization": "Bearer sk-xxx",
    "Content-Type": "application/json",
}
```

`json body` 是 HTTP 请求真正携带的“业务数据”，也就是你希望服务端处理的内容。例如调用大模型时，用户问题、模型名称、对话消息一般放在 body 里：

```
json_body = {
    "model": "gpt-4.1-mini",
    "messages": [
        {"role": "user", "content": "你好"}
    ],
}
```

调用大模型 API 时，认证信息通常放在 `headers` 里，是因为 API 服务端会先检查你有没有权限访问接口；而真正要模型处理的内容放在 `json body` 里。

一句话总结：

```
headers 管“请求身份和格式”，json body 管“业务内容”。
```

2.**`请求超时：https://httpbin.org/post` 的排查顺序**

- 检查网络是否可用，先确认浏览器能不能打开，如果浏览器都打不开，说明不是代码问题，优先检查网络、代理、VPN、防火墙

- 检查 URL 是否写错，确认代码里是不是：

```
url="https://httpbin.org/post"
```

常见错误包括少写 `https://`、拼错域名、把 `/post` 写成 `/posts`。

- 检查`timeout_secondes`是否太短
- 检查服务器端是否临时不可用，即使你的代码没问题，测试接口也可能临时慢或不可用。可以稍后重试，或者换成：

```
https://httpbin.org/get
```

做一个 GET 请求验证。

比较完整的排查表达可以这样写：

```
我会先确认本机网络是否能访问 httpbin，再检查 URL 是否完整且路径正确；
然后调整 timeout_seconds 以排除本地超时设置问题；
如果仍然失败，再换 GET 接口或稍后重试，判断是不是服务端临时不可用。
```



## Day3

大模型 API 调用本质是一次带认证信息的HTTP `POST`  请求，程序需要把用户输入组织成模型能理解的 `messages`，发送给模型服务，再把模型回答解析出来。

容易踩坑的是：不知道 `headers` 放认证、`messages` 放对话、`model` 放模型名；还有就是 API 返回结构较深，容易取错字段。

核心技术拆解：

```
用户输入
  -> main.py 负责命令行交互
  -> history.py 保存用户消息
  -> llm_client.py 组织 messages 和模型请求
  -> http_client.py 负责真正发送 HTTP 请求
  -> llm_client.py 解析模型回复
  -> history.py 保存 assistant 回复
  -> main.py 打印结果
```

今天要新增 `llm_client.py`，它是“业务客户端”，不是简单把请求代码塞进 `main.py`。把“模型请求细节”封装起来，让 `main.py` 只关心“用户问了什么、模型答了什么”。



### 问题

**1.概念解释**

请解释 [[LLM messages 结构]] 中 `system` 和 `user` 两种 `role` 的区别，并说明为什么今天代码里要先放一条 `system` 消息。

- `system` 和 `user` 都是 `messages` 里的消息角色，但职责不同。`system` 表示对模型的全局行为约束。它通常放在最前面，用来告诉模型“你应该以什么身份、什么风格、什么边界来回答”。`user` 表示用户真实输入的问题或指令。

```
system 负责规定模型怎么回答；
user 负责提供这一次要回答什么。
```



**2.Bug 排查题**

如果运行后报错 `HTTP 状态码错误：401`，请按顺序排查：`.env` 是否加载、`LLM_API_KEY` 是否正确、`Authorization` 是否写成 `Bearer xxx`、当前账号或服务商 Key 是否可用。

- 运行过程并未出现 `401`，但是出现了`503`和`429`

```
(.venv) PS D:\_Software_Projects\codex\ai_agent_daily_mentor\week1_llm_cli> python main.py
╭─────────────────────────── 配置检查 ───────────────────────────╮
│ 模型配置读取成功                                               │
│ 模型: gemini-3.5-flash                                         │
│ 地址: https://generativelanguage.googleapis.com/v1beta/openai/ │
╰────────────────────────────────────────────────────────────────╯
请输入您的问题：你好啊
运行失败: HTTP 状态码错误：503，url=https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
```

更换`.env`中`LM_MODEL="gemini-3-flash-preview"`（模型名可能不正确）为`LLM_MODEL="gemini-3.5-flash"`，仍然是503，大概率是 Gemini 服务临时容量问题。

```
───────────────── 配置检查 ─────────────────╮
│ 模型配置读取成功                           │
│ 模型: glm-5                                │
│ 地址: https://open.bigmodel.cn/api/paas/v4 │
╰────────────────────────────────────────────╯
请输入您的问题：你好
运行失败: HTTP 状态码错误：429，url=https://open.bigmodel.cn/api/paas/v4/chat/completions
```

当前账号额度/免费额度耗尽，账号并无模型glm-5额度，更改`LLM_MODEL=glm-5`为`LLM_MODEL=glm-4.7`后解决该问题。



## Day4

异步编程解决的是“多个网络请求等待时间叠加”的问题。LLM 调用、RAG 检索、Embedding、评分接口都可能很慢，如果全部串行执行，用户会明显等待。因为后续 Agent 工程经常需要同时调用多个工具、多个模型请求或多个检索任务。容易踩坑的是：以为写了 `async def` 就自动并发，但如果没有 `await`、没有 `asyncio.gather()`、底层仍用同步请求，性能不会变好。

核心技术拆解：

```
同步调用：
问题 1 -> 等模型返回 -> 问题 2 -> 等模型返回 -> 问题 3 -> 等模型返回

异步并发：
问题 1 ┐
问题 2 ├-> 同时发出请求 -> 等最慢的那个返回 -> 汇总结果
问题 3 ┘
```

项目链路：

```
async_demo.py
  -> 准备多个用户问题
  -> async_llm_client.py 并发调用模型
  -> 统计总耗时
  -> 输出每个问题的回答
  -> 为 Day5 的 LLM CLI 工具做并发能力准备
```

把异步逻辑单独放进 `async_llm_client.py`，不要污染 Day3 已经可用的同步 `llm_client.py`。这样做的原因是：同步版本适合单轮 CLI，异步版本适合批量请求、并发评估、多个工具调用。容易踩坑的是没有限制并发数量，导致触发 `429` 限流；或者某一个请求失败后，整个程序报错退出，没有留下可排查信息。



## Day5

- `main.py`的执行顺序

```
1.load_seetings() 读取api_key,base_url,model配置
2.input 接收用户输入并使用append_message保存信息
3.call_llm() 调用大模型
	3.1 build_user_message() 构建用户信息
	3.2 声明 url 和 headers
	3.3 判断 temperature 范围是否合法
	3.4 声明请求request_body
	3.5 request_json() 发送HTTP请求，并把JSON响应解析成字典
	3.6 parse_assistant_message() 从大模型的JSON回复中获取大模型的文本问答
4. append_message() 保存模型回答形成对话
5. load_history() 加载历史对话消息并打印历史消息数
```

- `main.py`如果直接写HTTP细节会导致文件臃肿，应该把`main.py`当作程序的入口，同时也当作项目的"入口层"，而HTTP细节属于“业务层”，应当与`main.py`中的代码区分开来。



### 问题

- 概念解释：请解释 [[命令行参数解析]] 的作用。为什么今天要用 `--message`，而不是每次都在代码里手动改问题？

```
`命令行参数解析`通过指定参数给用户选择，从而可以保护代码。使用`--message`而不是每次在代码里手动改问题同样也有保护代码不泄露同时也避免了反复在代码中修改从而导致代码出错，减少维护压力。
```

```
命令行参数解析的作用，是把用户在终端输入的参数转换成程序内部可以使用的变量。

今天使用 `--message`，是为了把“用户输入的问题”和“程序源码”分开。这样每次提问时只需要改命令，不需要改 `main.py`，可以减少误改代码的风险，也方便复用、测试和写 README 使用说明。

例如：

python main.py --message "解释 async def"

这里 `"解释 async def"` 是运行时输入，不属于源码。CLI 工具应该让用户通过参数控制行为，而不是每次打开代码手动修改。
```



- 小实现题：给今天的 CLI 增加一个 `--show-history-only` 参数。要求：只打印历史记录，不调用大模型。你需要说明这个参数应该放在流程的哪个位置判断。

```
这个参数我放在了`args = parser.parse_args()`之后以及`user_message = normalize_message(args.message)`之前，首先需要有一个`parser`对象存在，既然不调用大模型，我认为可以直接省去用户输入信息这一步骤从而减少操作。
```

```

```



- Bug 排查题：如果执行 `python main.py --message "你好"` 后报错 `请使用 --message 传入问题`，你会优先检查哪三件事？请结合 [[异常处理]] 和 [[LLM CLI 项目总览]] 回答。

```
1.首先检查`--message'以及后面的字符串是否有拼写错误。2.检查parser.add_argument()对应的'--message'是否类型指定错误。3.检查函数normalize_message()中是否存在if判断出错。
```

```
如果执行 `python main.py --message "你好"` 后仍然报错 `请使用 --message 传入问题`，说明 `normalize_message(args.message)` 收到的是 `None`。

我会优先检查三件事：

1. 检查命令是否真的传对了参数名，例如是不是写成了 `--mesage`、`--Message`，或者引号使用错误。

2. 检查 `build_parser()` 里是否正确注册了参数：
   `parser.add_argument("-m", "--message", type=str, required=False, ...)`
   如果参数名写错，`argparse` 就不会把终端输入绑定到 `args.message`。

3. 在 `args = parser.parse_args()` 后临时打印 `args` 或 `args.message`，确认参数解析结果。如果这里已经是 `None`，问题在命令或 parser；如果这里有值，但进入 `normalize_message()` 后变成 None，就检查函数调用时是否传错变量。
```



## Day6

```
# LLM CLI Debug Checklist

## 1. 环境变量问题

现象：

- 提示缺少 `LLM_API_KEY`
- 提示缺少 `LLM_BASE_URL`
- 提示缺少 `LLM_MODEL`

排查：

1. 检查 `.env` 是否存在。
2. 检查变量名是否拼写正确。
3. 检查变量值是否为空。
4. 确认 `.env` 没有被错误提交到 Git。

## 2. 命令行参数问题

现象：

- 提示 `message 不能为空`
- 提示 `请使用 --message 传入问题`
- `--show-history-only` 仍然要求输入 message

排查：

1. 检查命令是否写成 `--message "你好"`。
2. 检查 `--show-history-only` 是否在 `normalize_message()` 之前判断。
3. 检查 `argparse` 是否正确注册参数。

## 3. API 请求失败

现象：

- `401`：API Key 错误或未生效。
- `429`：请求过多或额度不足。
- `503`：服务暂时不可用。

排查：

1. 检查 API Key。
2. 降低请求频率。
3. 稍后重试。
4. 使用 `--debug` 查看完整错误。

## 4. 历史记录问题

现象：

- 历史文件为空时报错。
- `--history-limit -1` 行为异常。

排查：

1. 检查 `load_history()` 是否能处理空文件。
2. 检查 `history-limit` 是否做了负数校验。
3. 检查 `data/history.json` 是否是合法 JSON。
```



### 问题

- 概念解释：请解释 [[代码重构]] 和“重新写一遍代码”的区别。为什么今天要把 `main.py` 拆薄？





- 小实现题：请给今天的代码增加一个 `--debug` 参数。要求：普通模式只显示友好错误；debug 模式遇到未知错误时显示完整 traceback。说明你会把这个判断放在哪个函数里。





- Bug 排查题：如果执行 `python main.py --show-history-only --history-limit 5` 时仍然提示 `请使用 --message 传入问题`，说明流程顺序哪里错了？请结合 [[命令行参数解析]] 和 [[异常处理]] 说明排查步骤。





# Week2





## Day8

###### [[FastAPI 项目结构]]

从 CLI 工具进入后端服务

目标从 `LLM CLI 调用工具` 过渡到 `Agent 后端服务骨架`。CLI 是“用户在终端输入命令”，后端服务是“别人通过 HTTP 请求调用你的程序”。后面做 `AI-Interview` 时，前端页面、测试工具、其他服务都不会直接运行你的 `main.py`，而是通过接口访问你的后端。

`FastAPI` 是一个 Python Web 框架。你可以先把它理解成：它负责接收 HTTP 请求，把请求交给 Python 函数处理，再把函数返回值变成 HTTP 响应。

###### [[FastAPI 路由]] + [[Pydantic 数据校验]]

让接口输入输出有结构

`Pydantic` 是数据校验工具。它可以规定请求体里必须有什么字段、字段是什么类型。例如 `message` 必须是字符串，不能是空内容。

**LLM 应用很容易收到混乱输入。没有数据校验，你的业务代码里会到处写 `if message is None`。有了 Pydantic，接口入口就能先挡掉不合法数据。**

**查询状态用 `GET`，提交一段用户消息让后端处理，用 `POST`。**



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



## Day9

###### Pydantic 数据校验

`Pydantic` 的作用是：在请求进入业务函数之前，先检查数据结构、字段类型、长度限制和格式规则。

你可以把它理解成“接口门卫”。比如用户调用 `/api/v1/chat` 时传：

```
{
  "message": ""
}
```

后端不应该把空内容交给大模型，而应该在入口处直接拦截。LLM 接口很容易收到空消息、超长消息、缺字段、字段类型错误。如果没有校验，业务代码会堆满 `if` 判断，而且错误返回不统一。容易踩的坑是：以为 `message: str` 就足够了。实际上，`str` 只能保证“它是字符串”，不能保证“它不是空字符串”“它没有超长”“它符合业务规则”。

###### 统一响应格式 + FastAPI 422 错误

统一响应格式是指：接口成功时返回固定结构，失败时也返回固定结构。比如成功返回：

```
{
  "success": true,
  "data": {...},
  "error": null
}
```

失败返回：

```
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_MESSAGE",
    "message": "message 不能为空"
  }
}
```

前端或调用方不应该猜测接口返回结构。后续做 `AI-Interview` 时，简历解析、岗位匹配、RAG 出题、AI 评分都会有成功和失败情况，统一响应能让前后端协作更稳定。容易踩的坑是：有的接口返回字符串，有的返回字典，有的直接抛异常，导致调用方不好处理。今天要把 `/health`、`/api/v1/version`、`/api/v1/chat` 都收敛到相对统一的响应结构。

###### 具体任务

- 新增三个更通用的模型：`ErrorDetail` `ApiResponse` `VersionResponse`

- 理解 `Field()` 的常见参数： `min_length` `max_length` `description` `examples`

- 理解 `field_validator` 的作用：处理“类型正确但业务不合法”的数据，比如 `"   "`

###### 编码思路

先把接口边界做稳定：

1. `schemas.py` 负责定义“请求和响应长什么样”。
2. `main.py` 负责定义“哪个 URL 调哪个函数”。
3. `generate_fake_answer()` 负责临时生成假回答。
4. 明天只需要把 `generate_fake_answer()` 替换成真实 LLM 调用，接口输入输出不用大改。

这里重点解释两个概念：

- `BaseModel`：用 Python 类描述 JSON 数据结构。
- `field_validator`：在字段类型检查之后，再做业务规则检查。



##### 验收题

###### 1

**请解释 [[Pydantic 数据校验]] 在 FastAPI 请求流程中的作用。为什么 `message: str` 只能保证类型，不能保证内容有业务意义？**

```
HTTP 请求进入 FastAPI
-> FastAPI 根据路由找到对应函数
-> 读取请求体 JSON
-> 用 Pydantic 模型校验请求体
-> 校验通过，才执行你的路由函数
-> 路由函数返回响应
```

为什么 `message: str` 只能保证类型

下面这些都是字符串：

```
"你好"
"   "
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa..."
"随便乱输入"
```

它们的类型都是 `str`。所以只写：`message: str`只能说明：message 是字符串。不能说明：

```
message 不是空格。
message 长度合理。
message 是一个真实问题。
message 没有超过接口限制。
```

这就是“类型校验”和“业务校验”的区别。

可以这样分：

```
类型校验：这个值是什么类型？
业务校验：这个值在当前业务场景下有没有意义？
```

###### 2

**`field_validator` 不生效怎么排查**

第 1 层：路由函数有没有真的使用这个 Pydantic 模型

必须是这样：

```
@app.post("/api/v1/chat")
def chat(request: ChatRequest) -> ApiResponse:
    ...
```

如果你写成：

```
@app.post("/api/v1/chat")
def chat(request: dict) -> ApiResponse:
    ...
```

或者：

```
@app.post("/api/v1/chat")
def chat(message: str) -> ApiResponse:
    ...
```

那 `ChatRequest` 根本没参与校验，你写在 `ChatRequest` 里的 `field_validator` 自然不会执行。所以第一件事检查：

```
chat() 函数的参数类型是不是 ChatRequest？
```

第 2 层：`field_validator` 的字段名有没有写对

如果模型是：

```
class ChatRequest(BaseModel):
    message: str
```

校验器必须写：

```
@field_validator("message")
```

不能写成：

```
@field_validator("messages")
@field_validator("content")
```

字段名必须和模型字段完全一致。

所以第二件事检查：

```
@field_validator("message") 里的字段名，是否和 message 字段一致？
```

第 3 层：校验函数有没有返回清洗后的值

正确写法：

```
@field_validator("message")
@classmethod
def validate_message_not_blank(cls, value: str) -> str:
    message = value.strip()

    if not message:
        raise ValueError("message 不能为空")

    return message
```

这里有两个关键点：

1. 空格要先 `strip()`。
2. 最后要 `return message`。

**更好的排查答案：**

```
如果 `@field_validator("message")` 写了，但传入 `"   "` 没有报错，我会检查三件事：

1. 路由函数是否真的使用了 `ChatRequest`，例如 `def chat(request: ChatRequest)`。如果写成 `dict` 或普通字符串，Pydantic 模型不会参与校验。

2. `field_validator` 里的字段名是否写对。模型字段叫 `message`，就必须写 `@field_validator("message")`，不能写成 `messages` 或其他名字。

3. 校验逻辑是否对空格字符串做了 `strip()`。`"   "` 本身是字符串，而且长度大于 0，所以必须先 `value.strip()`，再判断是否为空，并且最后要返回清洗后的 `message`。
```

补充一个很实用的调试方法：
你可以临时在 validator 里加一行打印：

```
print("validator 执行了，value =", repr(value))
```

然后重新请求接口。
如果终端没有打印，说明校验器根本没执行，优先查第 1 和第 2 点。
如果打印了但没报错，说明校验逻辑写错，查第 3 点。



## Day10

##### 验收题

###### 1

概念解释：请解释 [[LLMClient 封装]] 的作用。为什么不建议在 `app/main.py` 的路由函数里直接写 `httpx.post()`？

```text
LLMClient 封装是把“调用大模型 API 的细节”集中放到客户端层，比如构造 URL、headers、payload、发送 httpx 请求、处理超时和状态码、解析响应。
```



###### 2

小实现题：请给 `ChatRequest` 增加 `use_fake: bool = False`。当 `use_fake` 为 `True` 时调用 `generate_fake_answer()`，否则调用 `generate_llm_answer()`。说明这个判断应该放在 `main.py` 还是 `chat_service.py`，为什么。

```text
路由函数会变重
main.py 既要处理请求响应，又要处理 API Key、URL、headers、timeout、状态码、JSON 解析，后续难维护。

复用困难
后面简历解析、岗位匹配、面试评分都可能调用 LLM。如果 LLM 请求逻辑写在某个路由函数里，其他地方复用不了。

测试困难
路由测试会被真实网络影响。把 LLM 调用封装到 llm_client.py 后，可以单独测试 parse_assistant_message()，也可以用 mock 模拟 HTTP 请求。
```

```text
`use_fake` 的判断更适合放在 `chat_service.py`，因为它属于聊天业务策略：当前请求到底走假回答还是真实 LLM。`main.py` 是路由层，只应该接收请求、调用服务层、返回响应。

判断必须发生在调用模型之前。如果先同时调用 `generate_fake_answer()` 和 `generate_llm_answer()`，再根据 `use_fake` 选择结果，就会导致即使使用假回答，也仍然消耗真实 LLM 请求。
```



###### 3

Bug 排查题：如果调用 `/api/v1/chat` 返回 `ConfigError: 缺少环境变量：LLM_API_KEY`，你会按什么顺序检查？请结合 [[环境变量与 API Key]]、[[FastAPI 项目结构]] 和 [[异常处理]] 回答。

```text
如果返回 `ConfigError: 缺少环境变量：LLM_API_KEY`，我会按以下顺序检查：

1. 检查 `.env` 是否放在当前 FastAPI 项目根目录 `week2_agent_api/` 下，并确认我是从这个目录启动 `uvicorn app.main:app --reload`。

2. 检查 `.env` 中变量名是否完全正确，应该是 `LLM_API_KEY`，不能写成 `LLM_API_KEEY` 或其他名字。

3. 检查 `LLM_API_KEY` 的值是否为空。如果写成 `LLM_API_KEY=` 或只有空格，`load_settings()` 中 `.strip()` 后仍然会被判断为缺失。

4. 检查 `app/config.py` 中 `os.getenv("LLM_API_KEY", "")` 是否拼写正确。

5. 修改 `.env` 后重启 uvicorn，确保服务重新读取配置。
```



## Day 11

###### [[FastAPI 路由]] 模块化

用 `APIRouter` 拆掉臃肿的 `main.py`。`APIRouter` 可以理解成“小型 FastAPI 路由容器”。它解决的问题是：当接口越来越多时，如果所有 `@app.get()`、`@app.post()` 都写在 `main.py`，入口文件会重新变臃肿。

后续 `AI-Interview` 会有很多接口，例如简历解析、岗位匹配、面试题生成、评分报告。如果不提前拆路由，项目会很快变乱。

容易踩的坑是：分不清 `app = FastAPI()` 和 `router = APIRouter()`。简单记住：`FastAPI()` 是整个应用；`APIRouter()` 是某一组接口；最后用 `app.include_router()` 把路由组注册到应用里。

###### [[异常处理]] 全局化

不要每个路由都重复 `try/except`

现在的路由函数里可能有：

```
try:
    ...
except AppError as error:
    return make_error_response(...)
```

今天要把这类重复逻辑迁移到全局异常处理器中。全局异常处理器的作用是：只要代码里抛出指定异常，FastAPI 自动用统一格式返回错误。大模型服务会出现配置错误、请求超时、状态码错误、解析错误。如果每个路由都自己写一遍 `try/except`，重复多，容易漏，错误格式也容易不一致。

容易踩的坑是：把所有异常都吞掉。今天只处理你定义过的 `AppError`，未知异常仍然交给 FastAPI 变成 `500`，方便后续 Debug。

# -

每日自我验收题探讨，我有一些自己的想法，但是还需要你帮我进行更深入的解析

1.LLMClient封装将原先`main.py`拆分为路由层，客户端层，再加上已经封装好的客户端层，将整个业务划分清晰。为什么不建议在 `app/main.py` 的路由函数里直接写 `httpx.post()`？httpx.post属于客户端层的任务，不应该写在路由层。2.我在`chat_service.py`中添加了变量`USE_FAKE: bool = False`，具体调用`generate_fake_answer()`还是`generate_llm_answer()`的判断应该在`main.py->chat()`中，该判断要在调用模型之前而不是调用了得到了两个回复后再根据`USE_FAKE`去判断保留哪个。3.我会先检查`.env`中有无`LLM_API_KEEY`配置且检查api key是否正确；然后检查`load_settings()`函数里是否存在拼写错误；最后检查函数`call_llm()`中的异常检查是否编写错误。





