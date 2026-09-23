from openai import OpenAI


# API 키 읽기
with open("mykey.txt", "r", encoding="utf-8") as f:
    api_key = f.read().strip()


# Mindlogic API 연결
client = OpenAI(
    api_key=api_key,
    base_url="https://factchat-cloud.mindlogic.ai/v1/gateway"
)


def ask_ai(question):
    """
    사용자의 질문을 LLM에게 보내고
    AI의 답변을 반환하는 함수
    """

    response = client.chat.completions.create(
        model="gpt-5.6-luna",
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 'AI 오답 노트 챗봇'이야. "
                    "프로그래밍과 컴퓨터공학 공부를 도와줘. "
                    "어려운 내용도 초보자가 이해하기 쉽게 설명하고, "
                    "필요하면 간단한 예제 코드도 함께 보여줘."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content