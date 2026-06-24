from typing import Any

from app.config import Settings
from app.http_client import request_json
from app.exceptions import InputValidationError, LLMRequestError

Message = dict[str, str]

def build_user_message(user_text: str) -> list[Message]:
    """
    User input is wrapped into the messages structure required by the large model API
    """
    clean_text = user_text.strip()

    if not clean_text:
        raise InputValidationError("User input cannot be empty.")
    
    # The Chat Completions API requires messages to be lists, with each message having at least a role and content
    return [
        {
            "role": "system",
            "content": "你是一个使用Python编程语言的严谨的 AI Agent 学习助手,请用中文回答,并尽量解释清楚原因。",
        },
        {
            "role": "user",
            "content": clean_text,
        },
    ]

def parse_assistant_message(response_data:dict[str,Any]) -> str:
    """
    Parsing assistant's answer text from the large model response JSON
    """
    choices = response_data.get("choices")

    if not isinstance(choices, list) or not choices:
        raise LLMRequestError("There are no choices in the model response and the answer cannot be parsed.")
    
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise LLMRequestError("The first choice in the model response is not a dictionary structure.")
    
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise LLMRequestError("There is no message field in the model response.")
    
    content = message.get("content")
    if not isinstance(content, str):
        raise LLMRequestError("The model answers empty.")
    
    return content

def call_llm(
        settings: Settings, 
        user_text: str,
        temperature: float = 0.3,
    ) -> str:
    """
    Call the API and return the model answer
    """
    messages = build_user_message(user_text)

    url = f"{settings.base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json",
    }

    if temperature < 0 or temperature > 2:
        raise ValueError("Temperature must be between 0 and 2.")
    request_body = {
        "model": settings.model,
        "messages": messages,
        # The lower the temperature, the more stable the response
        "temperature": temperature,
    }
    
    response_data = request_json(
        method="POST", 
        url=url, 
        headers=headers, 
        json_body=request_body, 
        timeout_seconds=60.0,
    )

    return parse_assistant_message(response_data)
