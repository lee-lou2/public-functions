from openai import OpenAI
import io
import json

client = OpenAI()

# 파일 생성
data = {
    "custom_id": "request-1",
    "method": "POST",
    "url": "/v1/chat/completions",
    "body": {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"},
        ],
    },
}
file_content = json.dumps(data).encode("utf-8")
file_obj = client.files.create(file=io.BytesIO(file_content), purpose="assistants")

# 배치 생성
batch_obj = client.batches.create(
    input_file_id=file_obj.id, endpoint="/v1/chat/completions", completion_window="24h"
)

# ... 최대 24시간 소요

# 결과 조회
resp = client.batches.retrieve(batch_obj.id)
if resp.status == "completed":
    content = client.files.content(resp.output_file_id)
    # {"id": "batch_req_wnaDys", "custom_id": "request-2", "response": {"status_code": 200, "request_id": "req_c187b3", "body": {"id": "chatcmpl-9758Iw", "object": "chat.completion", "created": 1711475054, "model": "gpt-3.5-turbo", "choices": [{"index": 0, "message": {"role": "assistant", "content": "2 + 2 equals 4."}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 24, "completion_tokens": 15, "total_tokens": 39}, "system_fingerprint": null}}, "error": null}
