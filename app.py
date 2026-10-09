from flask import Flask, render_template, request, redirect, url_for
import markdown

from chatbot import ask_ai

from subject import (
    load_subjects,
    add_subject,
    delete_subject
)

from wrong_note import (
    save_note,
    load_notes,
    update_note,
    delete_note
)

from quiz import make_quiz


app = Flask(__name__)


from auth import install_auth
install_auth(app)

# ==========================================
# 홈
# ==========================================

@app.route("/")
def index():

    return render_template("index.html")


# ==========================================
# 질문하기
# ==========================================

@app.route("/question", methods=["GET", "POST"])
def question():

    subjects = load_subjects()

    answer = None
    answer_html = None
    user_question = ""

    if request.method == "POST":

        action = request.form.get("action")

        # ======================================
        # AI에게 질문
        # ======================================

        if action == "ask":

            user_question = request.form.get(
                "question",
                ""
            ).strip()

            if user_question:

                answer = ask_ai(
                    user_question
                )

                answer_html = markdown.markdown(
                    answer,
                    extensions=[
                        "fenced_code",
                        "tables"
                    ]
                )

        # ======================================
        # 오답 노트 저장
        # ======================================

        elif action == "save":

            selected_subject = request.form.get(
                "subject",
                ""
            )

            user_question = request.form.get(
                "question",
                ""
            )

            answer = request.form.get(
                "answer",
                ""
            )

            if (
                selected_subject
                and user_question
                and answer
            ):

                save_note(
                    selected_subject,
                    user_question,
                    answer
                )

                return redirect(
                    url_for(
                        "notes",
                        subject=selected_subject
                    )
                )

    return render_template(
        "question.html",
        subjects=subjects,
        answer=answer,
        answer_html=answer_html,
        question=user_question
    )


# ==========================================
# 오답 노트
# ==========================================

@app.route("/notes")
def notes():

    subjects = load_subjects()

    selected_subject = request.args.get(
        "subject",
        ""
    )

    note_list = []

    if selected_subject:

        note_list = load_notes(
            selected_subject
        )

        for note in note_list:

            note["answer_html"] = markdown.markdown(
                note["answer"],
                extensions=[
                    "fenced_code",
                    "tables"
                ]
            )

    return render_template(
        "notes.html",
        subjects=subjects,
        selected_subject=selected_subject,
        notes=note_list
    )


# ==========================================
# 오답 노트 수정
# ==========================================

@app.route("/notes/update", methods=["POST"])
def note_update():

    subject = request.form.get(
        "subject",
        ""
    )

    index_text = request.form.get(
        "index",
        ""
    )

    question = request.form.get(
        "question",
        ""
    ).strip()

    answer = request.form.get(
        "answer",
        ""
    ).strip()

    if (
        subject
        and index_text.isdigit()
        and question
        and answer
    ):

        update_note(
            subject,
            int(index_text),
            question,
            answer
        )

    return redirect(
        url_for(
            "notes",
            subject=subject
        )
    )


# ==========================================
# 이해도 확인 문제 생성
# ==========================================

@app.route("/notes/complete", methods=["POST"])
def note_complete():

    subject = request.form.get(
        "subject",
        ""
    )

    index_text = request.form.get(
        "index",
        ""
    )

    # ======================================
    # 잘못된 요청
    # ======================================

    if (
        not subject
        or not index_text.isdigit()
    ):

        return redirect(
            url_for(
                "notes",
                subject=subject
            )
        )

    index = int(index_text)

    note_list = load_notes(
        subject
    )

    # ======================================
    # 존재하지 않는 오답 번호
    # ======================================

    if (
        index < 0
        or index >= len(note_list)
    ):

        return redirect(
            url_for(
                "notes",
                subject=subject
            )
        )

    note = note_list[index]

    # ======================================
    # AI에게 이해도 확인 문제 요청
    # ======================================

    prompt = f"""
너는 'AI 오답 노트 챗봇'의 이해도 확인 문제 출제자입니다.

다음은 사용자가 공부하면서 저장한 오답 노트입니다.

[원래 질문]

{note["question"]}

[학습 내용]

{note["answer"]}


사용자가 이 내용을 단순히 외운 것이 아니라
실제로 이해했는지 확인할 수 있는 문제를
정확히 1개 만들어주세요.


========================================
문제 유형
========================================

아래 6가지 유형 중
현재 학습 내용에 가장 적절한 유형 하나를 선택하여
문제를 만들어주세요.

매번 단순히 개념을 설명하거나
코드 실행 결과만 묻는 방식으로 출제하지 마세요.


1. 개념 설명형

학습한 개념의 의미나 특징을
사용자가 자신의 말로 설명하도록 합니다.

예:
- 이 개념이 필요한 이유를 설명하세요.
- 두 개념의 차이를 설명하세요.
- 이 기능이 어떤 역할을 하는지 설명하세요.


2. 코드 예측형

간단한 코드를 제시하고
실행 결과 또는 코드의 동작을 예측하도록 합니다.

단순히 결과만 쓰게 하지 말고
필요한 경우 결과가 나오는 이유도 설명하도록 합니다.


3. 오류 수정형

학습 내용과 관련된
짧은 잘못된 코드 또는 잘못된 사용 예를 제시합니다.

사용자가 오류나 문제점을 찾고
올바르게 수정하도록 문제를 만듭니다.


4. 코드 작성형

학습한 개념을 직접 사용해야 하는
짧고 간단한 프로그래밍 상황을 제시합니다.

사용자가 필요한 코드를 직접 작성하도록 합니다.

너무 긴 프로그램 전체를 작성하게 하지 말고
핵심 개념을 확인할 수 있는 짧은 코드만 요구하세요.


5. 상황 적용형

실제 프로그래밍 또는 학습 상황을 제시하고
배운 개념을 어떻게 적용할지 판단하도록 합니다.

예:
- 어떤 자료구조가 적절한지 판단
- 어떤 기능을 사용해야 하는지 판단
- 주어진 상황에서 해결 방법 설명


6. 비교·판단형

두 가지 코드, 방법 또는 개념을 제시하고
어떤 것이 적절한지 선택한 뒤
그 이유를 설명하도록 합니다.


========================================
다양성 규칙
========================================

- 원래 오답 노트의 질문을 그대로 다시 묻지 마세요.

- 학습 내용을 단순히 다른 문장으로 바꿔서
  다시 질문하지 마세요.

- 항상
  "실행 결과와 이유를 설명하세요"
  형태로만 문제를 만들지 마세요.

- 코드 관련 학습 내용이라도
  코드 예측형만 사용하지 마세요.

- 오류 수정형, 코드 작성형,
  상황 적용형, 비교·판단형도 적극적으로 사용하세요.

- 개념 관련 학습 내용이라면
  억지로 코드 문제를 만들 필요는 없습니다.

- 저장된 학습 내용에서 실제로 확인할 수 있는
  범위 안에서 문제를 만들어주세요.

- 오답 노트에 없는 지나치게 어려운 개념을
  새롭게 추가하지 마세요.


========================================
난이도
========================================

- 대학생이 복습용으로 풀 수 있는 난이도로 만드세요.

- 너무 쉬운 단순 암기 문제는 피하세요.

- 그렇다고 여러 개념을 한 문제에 지나치게 많이
  섞어서 어렵게 만들지도 마세요.

- 한 문제에서 확인하려는 핵심 학습 내용은
  명확해야 합니다.


========================================
코드 출력 규칙
========================================

문제에 코드가 포함되는 경우
반드시 Markdown 코드 블록을 사용하세요.

Python 코드라면 다음 형식을 사용하세요.

~~~python
numbers = [10, 20, 30]
numbers.append(40)

for number in numbers:
    print(number)
~~~

중요:

- 여러 코드 명령문을 한 줄에 이어 붙이지 마세요.
- 실제 코드처럼 명령문마다 줄을 나누세요.
- for문, if문, while문 등의 들여쓰기를 유지하세요.
- 문제 설명과 코드 블록 사이에는 빈 줄을 넣으세요.
- 코드 블록을 일반 문장 안에 한 줄로 넣지 마세요.


========================================
최종 출력 규칙
========================================

- 문제는 정확히 1개만 출력하세요.
- 문제 유형 이름은 출력하지 마세요.
- 정답은 출력하지 마세요.
- 해설도 출력하지 마세요.
- 인사말이나 부가 설명도 출력하지 마세요.
- 학생에게 보여줄 실제 문제 내용만 출력하세요.
"""

    test_question = ask_ai(
        prompt
    )

    # ======================================
    # 이해도 문제 Markdown → HTML
    # ======================================

    test_question_html = markdown.markdown(
        test_question,
        extensions=[
            "fenced_code",
            "tables"
        ]
    )

    return render_template(
        "complete_test.html",
        subject=subject,
        note_index=index,
        note=note,
        test_question=test_question,
        test_question_html=test_question_html
    )


# ==========================================
# 이해도 확인 문제 채점
# ==========================================

@app.route(
    "/notes/complete/check",
    methods=["POST"]
)
def note_complete_check():

    subject = request.form.get(
        "subject",
        ""
    )

    index_text = request.form.get(
        "index",
        ""
    )

    test_question = request.form.get(
        "test_question",
        ""
    ).strip()

    user_answer = request.form.get(
        "user_answer",
        ""
    ).strip()

    # ======================================
    # 기본 값 검사
    # ======================================

    if (
        not subject
        or not index_text.isdigit()
        or not test_question
        or not user_answer
    ):

        return redirect(
            url_for(
                "notes",
                subject=subject
            )
        )

    index = int(index_text)

    note_list = load_notes(
        subject
    )

    # ======================================
    # 존재하지 않는 오답 번호
    # ======================================

    if (
        index < 0
        or index >= len(note_list)
    ):

        return redirect(
            url_for(
                "notes",
                subject=subject
            )
        )

    note = note_list[index]

    # ======================================
    # AI에게 채점 요청
    # ======================================

    prompt = f"""
다음은 학생의 오답 노트와
이해도 확인 문제, 학생의 답변입니다.

[오답 노트의 원래 질문]

{note["question"]}

[오답 노트의 학습 내용]

{note["answer"]}

[이해도 확인 문제]

{test_question}

[학생의 답변]

{user_answer}


학생이 핵심 개념을 제대로 이해하고 있는지 평가해주세요.


판정 기준:

1. 핵심 개념을 이해하고 설명했다면 통과입니다.

2. 표현이 학습 내용과 완전히 같지 않아도
   의미가 맞으면 통과입니다.

3. 사소한 표현 차이나 작은 실수는 허용합니다.

4. 핵심 개념을 잘못 이해했거나
   설명하지 못했다면 실패입니다.

5. 문제에서 여러 내용을 요구했다면
   중요한 요구 사항을 대부분 답해야 합니다.

6. 이유나 설명을 요구한 문제에서
   단순히 정답이나 결과만 적었다면
   충분히 이해했다고 판단하지 마세요.

7. 코드 작성 문제라면
   코드가 완전히 동일하지 않아도
   요구한 기능이 올바르게 동작하면 통과할 수 있습니다.

8. 오류 수정 문제라면
   핵심 오류를 찾고 올바른 수정 방법을 제시했는지
   확인해주세요.

9. 상황 적용 문제나 비교 문제라면
   선택뿐만 아니라 그 이유가 학습 내용에 맞는지도
   확인해주세요.


반드시 아래 형식으로만 답해주세요.


통과인 경우:

PASS
피드백: 학생이 잘 이해한 부분을 짧게 설명


실패인 경우:

FAIL
피드백: 부족하거나 잘못 이해한 부분을 짧게 설명
"""

    evaluation = ask_ai(
        prompt
    )

    # ======================================
    # PASS / FAIL 판정
    # ======================================

    evaluation_lines = (
        evaluation
        .strip()
        .splitlines()
    )

    if evaluation_lines:

        first_line = (
            evaluation_lines[0]
            .strip()
            .upper()
        )

    else:

        first_line = ""

    passed = first_line == "PASS"

    # ======================================
    # 통과한 경우 오답 노트 삭제
    # ======================================

    if passed:

        delete_note(
            subject,
            index
        )

    # ======================================
    # 결과 화면용 문제 Markdown 변환
    # ======================================

    test_question_html = markdown.markdown(
        test_question,
        extensions=[
            "fenced_code",
            "tables"
        ]
    )

    # ======================================
    # AI 응답에서 PASS / FAIL / 피드백: 제거
    # ======================================

    clean_feedback_lines = []

    for line in evaluation_lines:

        stripped_line = line.strip()

        if stripped_line.upper() in [
            "PASS",
            "FAIL"
        ]:

            continue

        if stripped_line.startswith(
            "피드백:"
        ):

            stripped_line = stripped_line.replace(
                "피드백:",
                "",
                1
            ).strip()

        if stripped_line:

            clean_feedback_lines.append(
                stripped_line
            )

    clean_feedback = "\n".join(
        clean_feedback_lines
    )

    # ======================================
    # AI가 형식을 이상하게 반환한 경우
    # ======================================

    if not clean_feedback:

        if passed:

            clean_feedback = (
                "핵심 내용을 잘 이해하고 있습니다."
            )

        else:

            clean_feedback = (
                "답변에서 핵심 내용을 충분히 확인하기 어렵습니다. "
                "학습 내용을 다시 확인해보세요."
            )

    # ======================================
    # 피드백 Markdown → HTML
    # ======================================

    evaluation_html = markdown.markdown(
        clean_feedback,
        extensions=[
            "fenced_code",
            "tables"
        ]
    )

    # ======================================
    # 결과 화면
    # ======================================

    return render_template(
        "complete_result.html",
        subject=subject,
        passed=passed,
        evaluation=evaluation,
        evaluation_html=evaluation_html,
        test_question=test_question,
        test_question_html=test_question_html,
        user_answer=user_answer
    )


# ==========================================
# 퀴즈
# ==========================================

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    subjects = load_subjects()

    selected_subject = ""

    note_list = []

    quiz_list = []

    quiz_mode = ""

    selected_indices = []

    # ======================================
    # GET
    # ======================================

    if request.method == "GET":

        selected_subject = request.args.get(
            "subject",
            ""
        )

        if selected_subject:

            note_list = load_notes(
                selected_subject
            )

    # ======================================
    # POST
    # ======================================

    elif request.method == "POST":

        selected_subject = request.form.get(
            "subject",
            ""
        )

        quiz_mode = request.form.get(
            "quiz_mode",
            "all"
        )

        if selected_subject:

            note_list = load_notes(
                selected_subject
            )

            # ==================================
            # 전체 오답 복습
            # ==================================

            if quiz_mode == "all":

                selected_notes = note_list

            # ==================================
            # 원하는 오답 선택
            # ==================================

            elif quiz_mode == "selected":

                selected_indices = (
                    request.form.getlist(
                        "note_indices"
                    )
                )

                selected_notes = []

                for index_text in selected_indices:

                    if index_text.isdigit():

                        index = int(
                            index_text
                        )

                        if (
                            0
                            <= index
                            < len(note_list)
                        ):

                            selected_notes.append(
                                note_list[index]
                            )

            else:

                selected_notes = []

            # ==================================
            # 선택된 오답이 있을 경우
            # ==================================

            if selected_notes:

                notes_text = ""

                for note in selected_notes:

                    notes_text += (
                        "질문: "
                        + note["question"]
                        + "\n"
                        + "답변: "
                        + note["answer"]
                        + "\n\n"
                    )

                # ==================================
                # AI 퀴즈 생성
                # ==================================

                quiz_list = make_quiz(
                    notes_text
                )

                # ==================================
                # 문제 Markdown → HTML
                # ==================================

                for item in quiz_list:

                    item["question_html"] = (
                        markdown.markdown(
                            item["question"],
                            extensions=[
                                "fenced_code"
                            ]
                        )
                    )

                    # ==================================
                    # 해설이 있는 경우 Markdown 처리
                    # ==================================

                    if item.get("explanation"):

                        item["explanation_html"] = (
                            markdown.markdown(
                                item["explanation"],
                                extensions=[
                                    "fenced_code"
                                ]
                            )
                        )

                    else:

                        item["explanation_html"] = ""

    return render_template(
        "quiz.html",
        subjects=subjects,
        selected_subject=selected_subject,
        notes=note_list,
        quiz=quiz_list,
        quiz_mode=quiz_mode,
        selected_indices=selected_indices
    )


# ==========================================
# 과목 관리
# ==========================================

@app.route("/subjects")
def subjects():

    subject_list = load_subjects()

    return render_template(
        "subjects.html",
        subjects=subject_list
    )


# ==========================================
# 과목 추가
# ==========================================

@app.route(
    "/subjects/add",
    methods=["POST"]
)
def subject_add():

    subject_name = request.form.get(
        "subject",
        ""
    ).strip()

    if subject_name:

        add_subject(
            subject_name
        )

    return redirect(
        url_for(
            "subjects"
        )
    )


# ==========================================
# 과목 삭제
# ==========================================

@app.route(
    "/subjects/delete",
    methods=["POST"]
)
def subject_delete():

    subject_name = request.form.get(
        "subject",
        ""
    )

    if subject_name:

        delete_subject(
            subject_name
        )

    return redirect(
        url_for(
            "subjects"
        )
    )


# ==========================================
# 실행
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )