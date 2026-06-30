# LLM CLI 调用工具

这是一个基于 Python 的最小 LLM 命令行调用工具，用于练习环境变量配置、HTTP 请求、大模型 API 调用、对话历史保存、CLI 参数解析、异常处理和单元测试。

## 功能

- 通过命令行向大模型发送问题
- 支持保存 user / assistant 对话历史
- 支持查看历史记录
- 支持 `--no-save` 跳过保存
- 支持 `--debug` 查看完整错误堆栈
- 提供本地单元测试

## 环境变量

请在项目根目录创建 `.env`：

```text
LLM_API_KEY=你的 API Key
LLM_BASE_URL=https://你的大模型服务地址/v1
LLM_MODEL=你的模型名
```



## 安装依赖

```
.venv\Scripts\Activate.ps1

pyhton -m install requirements.txt
```

## 运行

```
.\.venv\Scripts\python.exe main.py --message "请解释 async def"
```

只查看历史：

```
.\.venv\Scripts\python.exe main.py --show-history-only --history-limit 5
```

不保存本轮对话：

```
.\.venv\Scripts\python.exe main.py --message "你好" --no-save
```

开启 debug：

```
.\.venv\Scripts\python.exe main.py --message "你好" --debug
```