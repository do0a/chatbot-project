import os


# 오답 노트를 저장할 폴더
NOTE_FOLDER = "notes"


# ==========================================
# 오답 노트 폴더 만들기
# ==========================================

def create_note_folder():
    if not os.path.exists(NOTE_FOLDER):
        os.makedirs(NOTE_FOLDER)


# ==========================================
# 과목 이름을 파일 이름으로 사용
# ==========================================

def get_note_file(subject):
    create_note_folder()

    return os.path.join(
        NOTE_FOLDER,
        subject + ".txt"
    )


# ==========================================
# 오답 노트 저장
# ==========================================

def save_note(subject, question, answer):
    file_path = get_note_file(subject)

    with open(file_path, "a", encoding="utf-8") as f:

        f.write("\n")
        f.write("========================================\n")
        f.write("질문: " + question + "\n\n")
        f.write("AI 답변:\n")
        f.write(answer + "\n")
        f.write("========================================\n")

    return True


# ==========================================
# 오답 노트 불러오기
# ==========================================

def load_notes(subject):
    file_path = get_note_file(subject)

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    notes = []

    sections = content.split("========================================")

    for section in sections:
        section = section.strip()

        if not section:
            continue

        question = ""
        answer = ""

        if "질문:" in section and "AI 답변:" in section:
            question_part, answer_part = section.split("AI 답변:", 1)

            question = question_part.replace("질문:", "").strip()
            answer = answer_part.strip()

            notes.append({
                "question": question,
                "answer": answer
            })

    return notes