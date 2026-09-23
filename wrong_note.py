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

    # 아직 저장된 오답이 없는 경우
    if not os.path.exists(file_path):
        return ""

    with open(file_path, "r", encoding="utf-8") as f:
        notes = f.read()

    return notes