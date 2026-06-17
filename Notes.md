# Week1

## Day2

### 内容

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



### 每日自我验收题

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