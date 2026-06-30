from app.clients.llm_client import parse_assistant_message

if __name__ == "__main__":
    # 测试
    response_json1 = {"choices": [{"message": {"conten": ""}}]}
    response_json2 = {"choices": [{"message": {"content": 2}}]}
    response_json3 = {"choices": [{"message": {"content": ""}}]}

    # parse_assistant_message(response_json1)
    # parse_assistant_message(response_json2)
    parse_assistant_message(response_json3)
