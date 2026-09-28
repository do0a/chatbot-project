from flask import Flask, render_template, request, redirect
from chatbot import ask_ai
from wrong_note import save_note, load_notes
from subject import load_subjects, add_subject, delete_subject
from quiz import make_quiz
import markdown


app = Flask(__name__)


# ==============================
# 홈
# ==============================

@app.route("/")
def home():

    return render_template("index.html")


# ==============================
# 질문하기
# ==============================

@app.route("/question", methods=["GET", "POST"])
def question():

    answer = None
    user_question = None
    saved = False

    subjects = load_subjects()

    selected_subject = ""

    if request.method == "POST":

        user_question = request.form.get(
            "question",
            ""
        ).strip()

        selected_subject = request.form.get(
            "subject",
            ""
        ).strip()


        # ==============================
        # 오답 노트 저장
        # ==============================

        if request.form.get("save") == "yes":

            answer = request.form.get(
                "answer",
                ""
            )

            if selected_subject:

                save_note(
                    selected_subject,
                    user_question,
                    answer
                )

                saved = True


        # ==============================
        # AI에게 질문
        # ==============================

        else:

            if user_question:

                answer = ask_ai(
                    user_question
                )


    return render_template(
        "question.html",
        answer=answer,
        user_question=user_question,
        saved=saved,
        subjects=subjects,
        selected_subject=selected_subject
    )


# ==============================
# 오답 노트
# ==============================

@app.route("/notes")
def notes():

    subjects = load_subjects()

    selected_subject = request.args.get(
        "subject",
        ""
    ).strip()


    notes = []


    # 과목이 선택된 경우
    if selected_subject:

        notes = load_notes(
            selected_subject
        )


        # Markdown → HTML
        for note in notes:

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
        notes=notes
    )


# ==============================
# 퀴즈
# ==============================

@app.route("/quiz")
def quiz():

    subjects = load_subjects()

    selected_subject = request.args.get(
        "subject",
        ""
    ).strip()


    quiz_data = []


    # 과목을 선택했을 때만 퀴즈 생성
    if selected_subject:

        notes = load_notes(
            selected_subject
        )


        notes_text = "\n\n".join(
            [
                "질문: " + note["question"] +
                "\nAI 답변: " + note["answer"]
                for note in notes
            ]
        )


        if notes_text:

            quiz_data = make_quiz(
                notes_text
            )


    return render_template(
        "quiz.html",
        quiz=quiz_data,
        subjects=subjects,
        selected_subject=selected_subject
    )


# ==============================
# 과목 관리
# ==============================

@app.route("/subjects")
def subjects():

    subjects = load_subjects()

    return render_template(
        "subjects.html",
        subjects=subjects
    )


# ==============================
# 과목 추가
# ==============================

@app.route(
    "/subjects/add",
    methods=["POST"]
)
def subjects_add():

    subject = request.form.get(
        "subject",
        ""
    ).strip()


    if subject:

        add_subject(
            subject
        )


    return redirect(
        "/subjects"
    )


# ==============================
# 과목 삭제
# ==============================

@app.route(
    "/subjects/delete",
    methods=["POST"]
)
def subjects_delete():

    subject = request.form.get(
        "subject",
        ""
    ).strip()


    if subject:

        delete_subject(
            subject
        )


    return redirect(
        "/subjects"
    )


# ==============================
# 프로그램 실행
# ==============================

if __name__ == "__main__":

    app.run(
        debug=True
    )