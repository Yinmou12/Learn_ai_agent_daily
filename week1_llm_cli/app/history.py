from pathlib import Path
import json

Message=dict[str,str]

def validate_message(message:Message)->None:
    """校验一条信息是否符合最小对话格式"""
    role=message.get("role")
    content=message.get("content")

    if role not in {"system","user","assistant"}:
        raise ValueError(f"非法 role: {role}")
    
    if not isinstance(content, str) or not content.strip():
        raise ValueError(f"content 必须是非空字符串")
    
def load_history(path:Path=Path("data") / "history.json") -> list[Message]:
    """读取历史信息,文件不存在时返回空列表"""
    if not path.exists():
        return []
    
    try:
        raw_text=path.read_text(encoding="utf-8").strip()
        if not raw_text:
            return []
        data=json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"历史文件不是合法 JSON: {path}") from exc
    except OSError as exc:
        raise RuntimeError(f"读取历史文件失败: {path}") from exc
    
    if not isinstance(data, list):
        raise RuntimeError("历史文件顶层结构必须是列表")
    
    messages: list[Message] = []
    for item in data:
        if not isinstance(item, dict):
            raise RuntimeError("历史信息必须是字典结构")
        
        message={
            "role":str(item.get("role","")),
            "content":str(item.get("content","")),
        }
        validate_message(message)
        messages.append(message)

    return messages

def save_history(messages:list[Message],path:Path=Path("data") / "history.json")->None:
    """把完整历史消息写入 JSON 文件"""
    for message in messages:
        validate_message(message)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(messages,ensure_ascii=False,indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise RuntimeError(f"保存历史文件失败: {path}") from exc
    
def append_message(message:Message,path:Path=Path("data") / "history.json") -> list[Message]:
    """追加一条消息, 并返回更新后的完整历史"""
    validate_message(message)
    messages=load_history(path)
    messages.append(message)
    save_history(messages,path)
    return messages


def get_last_message(path:Path=Path("data") / "history.json")->Message|None:
    """获取最后一条消息"""
    messages = load_history(path)
    if not messages:
        raise ValueError("暂无历史消息")
    
    return messages[-1]