import os

import openai
import json


# API 키 설정
openai.api_key = os.environ.get("OPENAI_API_KEY")


# 예약 취소하는 함수
def cancel_reservation_by_name(name: str, number: int = 1):
    reservations = [
        {"name": "김철수", "number": 3},
        {"name": "김영희", "number": 2},
    ]
    for reservation in reservations:
        if reservation["name"] == name and reservation["number"] == number:
            reservations.remove(reservation)
            return "예약이 취소되었습니다."
    return "예약을 찾을 수 없습니다."


def function_conversation(prompt: str):
    """함수 대화"""
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[{"role": "user", "content": prompt}],
        functions=[
            {
                "name": "get_restaurant_reservation",
                "description": "식당 예약을 조회하는 함수",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "restaurant": {
                            "type": "string",
                            "description": "식당 이름을 입력해주세요",
                        },
                        "menu": {
                            "type": "string",
                            "description": "메뉴를 입력해주세요",
                        },
                        "time": {
                            "type": "string",
                            "description": "예약 시간을 입력해주세요",
                        },
                        "number": {
                            "type": "integer",
                            "description": "예약 인원을 입력해주세요",
                            "default": 1,
                            "max_value": 100
                        },
                    },
                    "required": ["restaurant", "date", "time", "number"],
                },
            },
            # 예약자 이름으로 예약 취소하는 함수
            {
                "name": "cancel_reservation_by_name",
                "description": "예약자 이름으로 예약을 취소하는 함수",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "예약자 이름을 입력해주세요",
                        },
                        "number": {
                            "type": "integer",
                            "description": "예약 인원을 입력해주세요",
                            "default": 1,
                        },
                    },
                    "required": ["name"],
                },
            },
        ],
        function_call="auto",
    )
    reply_content = completion.choices[0].message.to_dict()
    function = reply_content["function_call"]["name"]
    string_arguments = reply_content["function_call"]["arguments"]
    arguments = json.loads(string_arguments)
    print(f"[ 질문에서 알아낸 정보 ]\n▶️ prompt : {prompt}\n▶️ function name : {function}\n▶️ arguments : {arguments})")
    if function == "cancel_reservation_by_name":
        print(cancel_reservation_by_name(**arguments))


# # 질문1
# function_conversation(
#     "안녕하세요. 거기 김밥 천국 맞나요? "
#     "저 오늘 예약하고 싶은데요. 3명? 아 아니다 2명 가려구요. "
#     "메뉴는 ... 야 너 뭐 먹을래? 김밥? 김밥이랑 라면 하나 주세요. "
#     "이따 저녁 3시쯤 도착 예정입니다."
# )

# 질문2
function_conversation(
    "안녕하세요. 저 오늘 예약 했었는데. 혹시 예약 취소 가능할까요? "
    "김영희로 예약했었어요. 사정이 좀 있어서요. "
    "아! 2명 가려고 했었어요"
)
