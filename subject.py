import os


# 과목을 저장할 파일
SUBJECT_FILE = "subjects.txt"


# ==========================================
# 과목 목록 불러오기
# ==========================================

def load_subjects():
    if not os.path.exists(SUBJECT_FILE):
        return []

    with open(SUBJECT_FILE, "r", encoding="utf-8") as f:
        subjects = [line.strip() for line in f if line.strip()]

    return subjects


# ==========================================
# 과목 추가
# ==========================================

def add_subject(subject):
    subjects = load_subjects()

    # 이미 있는 과목인지 확인
    if subject in subjects:
        return False

    subjects.append(subject)

    with open(SUBJECT_FILE, "w", encoding="utf-8") as f:
        for item in subjects:
            f.write(item + "\n")

    return True


# ==========================================
# 과목 삭제
# ==========================================

def delete_subject(subject):
    subjects = load_subjects()

    if subject not in subjects:
        return False

    subjects.remove(subject)

    with open(SUBJECT_FILE, "w", encoding="utf-8") as f:
        for item in subjects:
            f.write(item + "\n")

    return True