import json

temp = (
    [
        {
            "score": 29,
            "matched_terms": ["fastapi", "depends", "依赖注入"],
            "question": {
                "id": 5,
                "question": "FastAPI 中 Depends 的作用是什么？",
                "reference_answer": "Depends 用于声明依赖注入，让路由函数自动获取数据库 Session、当前用户、配置对象等公共依赖。",
                "key_points": [
                    "依赖注入",
                    "复用公共逻辑",
                    "认证",
                    "数据库 Session",
                ],
                "difficulty": "medium",
                "tags": ["FastAPI", "Depends"],
                "created_at": "2026-07-19T17:19:01.323935",
            },
        },
        {
            "score": 29,
            "matched_terms": ["fastapi", "depends", "依赖注入"],
            "question": {
                "id": 2,
                "question": "请解释 FastAPI 中 Depends 的作用。",
                "reference_answer": "Depends 用于声明依赖注入，让路由函数自动获取数据库连接、当前用户等对象。",
                "key_points": [
                    "依赖注入",
                    "复用公共逻辑",
                    "常用于认证和数据库 Session",
                ],
                "difficulty": "medium",
                "tags": ["FastAPI", "Depends", "后端分层"],
                "created_at": "2026-07-19T16:45:49.549659",
            },
        },
        {
            "score": 29,
            "matched_terms": ["fastapi", "depends", "依赖注入"],
            "question": {
                "id": 1,
                "question": "请解释 FastAPI 中 Depends 的作用。",
                "reference_answer": "Depends 用于声明依赖注入，让路由函数自动获取数据库连接、当前用户等对象。",
                "key_points": [
                    "依赖注入",
                    "复用公共逻辑",
                    "常用于认证和数据库 Session",
                ],
                "difficulty": "medium",
                "tags": ["FastAPI", "Depends", "后端分层"],
                "created_at": "2026-07-19T16:45:22.910641",
            },
        },
    ],
)


temp_json = [json.dumps(item, ensure_ascii=False) for item in temp]
print(temp_json)
print(type(temp_json))
