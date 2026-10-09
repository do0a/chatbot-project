import os
import json
from openai import OpenAI


# ==========================================
# API 키 불러오기
# ==========================================

api_key = os.getenv("FACTCHAT_API_KEY")

if not api_key:
    try:
        with open("mykey.txt", "r", encoding="utf-8") as f:
            api_key = f.read().strip()

    except FileNotFoundError:
        raise RuntimeError(
            "API 키를 찾을 수 없습니다. "
            "FACTCHAT_API_KEY 환경변수 또는 "
            "mykey.txt 파일을 확인해주세요."
        )


# ==========================================
# OpenAI Client
# ==========================================

client = OpenAI(
    api_key=api_key,
    base_url="https://factchat-cloud.mindlogic.ai/v1/gateway"
)


# ==========================================
# 퀴즈 생성
# ==========================================

def make_quiz(notes):

    if not notes.strip():
        return []


    system_prompt = '''
너는 "AI 오답 노트 챗봇"의 복습 퀴즈 출제자야.

학생이 저장한 오답 노트를 바탕으로
객관식 복습 퀴즈를 정확히 3문제 만들어.

각 문제에는 반드시 다음 정보가 있어야 해.

- question: 문제
- options: 보기 4개
- answer: 정답 번호
- explanation: 정답에 대한 짧은 해설


========================================
1번 문제 - 개념 이해형
========================================

오답 노트의 핵심 개념을 이해했는지 확인해.

다음과 같은 유형을 활용할 수 있어.

- 개념의 의미
- 개념의 특징
- 개념의 역할
- 두 개념의 차이
- 올바른 설명 찾기
- 잘못된 설명 찾기

오답 노트의 질문을 그대로 복사해서
문제로 만들지 마.


========================================
2번 문제 - 코드 이해 / 예측형
========================================

프로그래밍 관련 내용이라면
간단한 코드 예제를 이용해 문제를 만들어.

가능한 문제 유형:

- 코드 실행 결과 예측
- 코드의 동작 이해
- 오류 원인 찾기
- 빈칸에 들어갈 코드 찾기
- 적절한 코드 선택

코드가 문제에 들어간다면
반드시 Markdown 코드 블록을 사용해.

예시는 다음과 같은 형태야.

다음 Python 코드의 실행 결과로 알맞은 것은?

~~~python
numbers = [1, 2]
numbers.append(3)
print(numbers)
~~~

중요:

- 코드 명령문을 한 줄에 이어 붙이지 마.
- 실제 코드처럼 줄을 나눠서 작성해.
- 들여쓰기가 필요한 코드는 들여쓰기를 유지해.
- 코드 앞뒤에는 일반 문제 문장과 구분되도록 줄바꿈을 넣어.

오답 노트 내용이 코드와 전혀 관련 없다면
억지로 코드 문제를 만들지 않아도 돼.

그 경우 예시 해석 문제나
다른 형태의 이해 문제로 바꿔.


========================================
3번 문제 - 응용 / 상황형
========================================

학생이 배운 내용을 새로운 상황에
적용할 수 있는지 확인하는 문제를 만들어.

가능한 문제 유형:

- 실제 프로그래밍 상황
- 적절한 자료구조 선택
- 적절한 기능 선택
- 문제 해결 방법 판단
- 새로운 예시에 개념 적용

단순 암기 문제가 아니라
내용을 이해해야 풀 수 있도록 만들어.


========================================
문제 다양성 규칙
========================================

3문제는 서로 다른 방식으로 출제해.

같은 내용을 표현만 조금 바꿔서
반복해서 묻지 마.

오답 노트에 있는 질문 문장을
그대로 문제로 복사하지 마.

저장된 오답 노트가 여러 개라면
특정 오답 하나에만 집중하지 말고
가능한 한 서로 다른 내용을 활용해.

특정 오답 하나만 제공된 경우에는
그 내용을 서로 다른 관점으로 출제해.

예를 들어 같은 개념이라도

1번은 개념 이해,
2번은 코드 또는 예시,
3번은 실제 활용

방식으로 다르게 출제해.


========================================
객관식 규칙
========================================

각 문제에는 반드시 보기 4개가 있어야 해.

각 문제의 정답은 정확히 하나만 존재해야 해.

틀린 보기도 너무 엉뚱하게 만들지 말고
학생이 실제로 고민할 만한 내용으로 만들어.

answer는 정답 보기 번호야.

answer에는 반드시
1, 2, 3, 4 중 하나만 사용해.

정답 위치가 세 문제 모두
같은 번호가 되지 않도록 다양하게 배치해.


========================================
해설 규칙
========================================

모든 문제에는 explanation을 반드시 작성해.

해설은 학생이 문제를 틀렸을 때
왜 그 답이 정답인지 이해할 수 있도록 작성해.

해설은 너무 길지 않게
2~4문장 정도로 작성해.

단순히

"2번이 정답입니다."

처럼 정답 번호만 알려주지 마.

반드시 핵심 개념과
정답인 이유를 설명해.

코드 문제라면 필요한 경우
코드가 실행되는 순서도 설명해.

학생이 틀린 이유를 다시 공부할 수 있는
복습용 해설을 작성해.


========================================
출력 형식
========================================

반드시 JSON 배열만 반환해.

형식은 다음과 같아.

[
    {
        "question": "문제 내용",
        "options": [
            "보기 1",
            "보기 2",
            "보기 3",
            "보기 4"
        ],
        "answer": 1,
        "explanation": "정답인 이유를 설명하는 짧은 해설"
    },
    {
        "question": "문제 내용",
        "options": [
            "보기 1",
            "보기 2",
            "보기 3",
            "보기 4"
        ],
        "answer": 2,
        "explanation": "정답인 이유를 설명하는 짧은 해설"
    },
    {
        "question": "문제 내용",
        "options": [
            "보기 1",
            "보기 2",
            "보기 3",
            "보기 4"
        ],
        "answer": 3,
        "explanation": "정답인 이유를 설명하는 짧은 해설"
    }
]

JSON 이외의 설명은 작성하지 마.
인사말도 작성하지 마.
JSON 전체를 Markdown 코드 블록으로 감싸지 마.

단,
question 안에 실제 코드가 필요한 경우에는
question 문자열 내부에서 Markdown 코드 블록을 사용할 수 있어.
'''


    user_prompt = (
        "다음은 학생이 저장한 오답 노트야.\n\n"
        "이 내용을 바탕으로 복습 문제 3개를 만들어줘.\n\n"
        "1번은 개념 이해형,\n"
        "2번은 코드 이해 또는 예측형,\n"
        "3번은 응용 또는 상황형으로 만들어줘.\n\n"
        "각 문제에는 학생이 틀렸을 때 확인할 수 있는 "
        "짧고 이해하기 쉬운 해설도 작성해줘.\n\n"
        "코드 문제가 있다면 코드를 한 줄에 붙이지 말고 "
        "실제 코드처럼 줄바꿈과 들여쓰기를 유지해줘.\n\n"
        "[오답 노트]\n\n"
        + notes
    )


    # ==========================================
    # AI 요청
    # ==========================================

    response = client.chat.completions.create(
        model="gpt-5.6-luna",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )


    # ==========================================
    # AI 응답 가져오기
    # ==========================================

    result = response.choices[0].message.content.strip()


    # ==========================================
    # JSON 전체를 코드 블록으로 감싼 경우 제거
    # ==========================================

    if result.startswith("```json"):
        result = result[7:]

    elif result.startswith("```"):
        result = result[3:]


    if result.endswith("```"):
        result = result[:-3]


    result = result.strip()


    # ==========================================
    # JSON 변환
    # ==========================================

    try:
        quiz = json.loads(result)

    except json.JSONDecodeError:

        print("퀴즈 데이터를 읽는 중 오류가 발생했습니다.")
        print("AI가 반환한 내용:")
        print(result)

        return []


    # ==========================================
    # 기본 데이터 검사
    # ==========================================

    if not isinstance(quiz, list):
        return []


    valid_quiz = []


    for item in quiz[:3]:

        if not isinstance(item, dict):
            continue


        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")
        explanation = item.get("explanation")


        # 질문 검사
        if not isinstance(question, str):
            continue

        if not question.strip():
            continue


        # 보기 검사
        if not isinstance(options, list):
            continue

        if len(options) != 4:
            continue

        if not all(
            isinstance(option, str)
            for option in options
        ):
            continue


        # 정답 검사
        if answer not in [1, 2, 3, 4]:
            continue


        # 해설 검사
        if not isinstance(explanation, str):
            explanation = "해설을 불러오지 못했습니다."

        if not explanation.strip():
            explanation = "해설을 불러오지 못했습니다."


        # 정상 문제 저장
        valid_quiz.append(
            {
                "question": question.strip(),
                "options": options,
                "answer": answer,
                "explanation": explanation.strip()
            }
        )


    return valid_quiz