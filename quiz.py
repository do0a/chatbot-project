import os
import json
from openai import OpenAI


# API 키 읽기
# Render에서는 환경변수 사용
api_key = os.getenv("FACTCHAT_API_KEY")

# 로컬 실행에서는 기존 mykey.txt 사용
if not api_key:
    try:
        with open("mykey.txt", "r", encoding="utf-8") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(
            "API 키를 찾을 수 없습니다. "
            "FACTCHAT_API_KEY 환경변수 또는 mykey.txt 파일을 확인해주세요."
        )


# Mindlogic API 연결
client = OpenAI(
    api_key=api_key,
    base_url="https://factchat-cloud.mindlogic.ai/v1/gateway"
)


def make_quiz(notes):
    """
    오답 노트 내용을 바탕으로
    AI가 객관식 퀴즈 3문제를 만드는 함수
    """

    if not notes.strip():
        return []

    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[
            {
                "role": "system",
                "content": """
너는 AI 오답 노트 챗봇의 퀴즈 출제자야.

학생이 저장한 오답 노트를 바탕으로
복습용 객관식 퀴즈 3문제를 만들어줘.

각 문제는 반드시 다음 형식의 JSON으로 만들어야 해.

[
    {
        "question": "문제 내용",
        "options": [
            "보기 1",
            "보기 2",
            "보기 3",
            "보기 4"
        ],
        "answer": 1
    }
]

주의사항:
- 문제는 반드시 3개
- 각 문제의 보기는 반드시 4개
- answer는 정답 보기의 번호
- answer는 1, 2, 3, 4 중 하나
- 학생이 실제로 풀 수 있도록 정답을 문제에 표시하지 말 것
- 오답 노트에 있는 내용을 중심으로 문제를 만들 것
- 너무 어려운 문제보다는 복습하기 좋은 문제를 만들 것
- JSON 이외의 설명은 작성하지 말 것
"""
            },
            {
                "role": "user",
                "content": (
                    "다음은 학생의 오답 노트야.\n\n"
                    + notes
                    + "\n\n"
                    "이 내용을 바탕으로 퀴즈를 만들어줘."
                )
            }
        ]
    )

    result = response.choices[0].message.content.strip()

    # AI가 ```json ... ``` 형태로 보내는 경우 제거
    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    try:
        quiz = json.loads(result)
        return quiz

    except json.JSONDecodeError:
        print("퀴즈 데이터를 읽는 중 오류가 발생했습니다.")
        print("AI가 반환한 내용:")
        print(result)

        return []