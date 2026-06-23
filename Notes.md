

# Week1

## 项目结构

```
weeik1_llm_cli/
├── app/
│   ├── __init__.py
│   ├── async_llm_client.py  职责只做异步大模型调用
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
├── test_env.py
├── test_http_client.py
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

