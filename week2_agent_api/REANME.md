# Week2 Agent Backend API

这是 Week2 的最小 FastAPI 后端骨架，用于把 Week1 的 CLI 能力逐步迁移成 HTTP API。

## 安装依赖

```powershell
python -m pip install fastapi uvicorn pydantic
```

### Day 8

--reload 表示开发模式下自动重载：修改代码后，服务会自动重启。

```
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

```
服务启动成功：是
/docs 可访问：是
/ 返回 404：因为你没写根路由
/favicon.ico 返回 404：浏览器自动请求图标，可以忽略
```

你现在应该优先访问：

```
http://127.0.0.1:8000/docs
```

而不是：

```
http://127.0.0.1:8000/
```



### Day 9

