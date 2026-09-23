from chatbot import ask_ai
from subject import load_subjects, add_subject, delete_subject
from wrong_note import save_note, load_notes
from quiz import make_quiz


def main():

    while True:

        print("\n================================")
        print("       AI 오답 노트 챗봇")
        print("================================")
        print("1. 질문하기")
        print("2. 과목 추가")
        print("3. 과목 삭제")
        print("4. 오답 노트 보기")
        print("5. 퀴즈 풀기")
        print("6. 종료")

        choice = input("\n선택: ")


        # ==========================================
        # 1. 질문하기
        # ==========================================

        if choice == "1":

            subjects = load_subjects()

            if not subjects:
                print("\n등록된 과목이 없습니다.")
                print("먼저 과목을 추가해 주세요.")
                continue


            print("\n[과목 목록]")

            for i, subject in enumerate(subjects, 1):
                print(f"{i}. {subject}")


            try:
                number = int(input("\n과목 번호: "))
                subject = subjects[number - 1]

            except (ValueError, IndexError):
                print("잘못된 번호입니다.")
                continue


            question = input("\n질문: ")


            print("\nAI가 답변을 생각하고 있습니다...\n")


            try:

                answer = ask_ai(question)

                print("========== AI 답변 ==========")
                print(answer)
                print("=============================")

            except Exception as e:

                print("\nAI 답변을 가져오는 중 오류가 발생했습니다.")
                print("오류 내용:", e)
                continue


            save = input("\n💾 오답 노트에 저장할까요? (y/n): ")


            if save.lower() == "y":

                save_note(subject, question, answer)

                print("오답 노트에 저장되었습니다!")


        # ==========================================
        # 2. 과목 추가
        # ==========================================

        elif choice == "2":

            subject = input("\n추가할 과목 이름: ").strip()


            if not subject:

                print("과목 이름을 입력해 주세요.")
                continue


            if add_subject(subject):

                print(f"'{subject}' 과목이 추가되었습니다.")

            else:

                print("이미 존재하는 과목입니다.")


        # ==========================================
        # 3. 과목 삭제
        # ==========================================

        elif choice == "3":

            subjects = load_subjects()


            if not subjects:

                print("\n삭제할 과목이 없습니다.")
                continue


            print("\n[과목 목록]")

            for i, subject in enumerate(subjects, 1):

                print(f"{i}. {subject}")


            try:

                number = int(input("\n삭제할 과목 번호: "))
                subject = subjects[number - 1]

            except (ValueError, IndexError):

                print("잘못된 번호입니다.")
                continue


            if delete_subject(subject):

                print(f"'{subject}' 과목이 삭제되었습니다.")

            else:

                print("과목 삭제에 실패했습니다.")


        # ==========================================
        # 4. 오답 노트 보기
        # ==========================================

        elif choice == "4":

            subjects = load_subjects()


            if not subjects:

                print("\n등록된 과목이 없습니다.")
                continue


            print("\n[과목 목록]")

            for i, subject in enumerate(subjects, 1):

                print(f"{i}. {subject}")


            try:

                number = int(input("\n볼 과목 번호: "))
                subject = subjects[number - 1]

            except (ValueError, IndexError):

                print("잘못된 번호입니다.")
                continue


            notes = load_notes(subject)


            if notes:

                print(f"\n========== {subject} 오답 노트 ==========")
                print(notes)
                print("========================================")

            else:

                print("\n저장된 오답 노트가 없습니다.")


        # ==========================================
        # 5. 퀴즈 풀기
        # ==========================================

        elif choice == "5":

            subjects = load_subjects()


            if not subjects:

                print("\n등록된 과목이 없습니다.")
                continue


            print("\n[퀴즈를 풀 과목 선택]")


            for i, subject in enumerate(subjects, 1):

                print(f"{i}. {subject}")


            try:

                number = int(input("\n과목 번호: "))
                subject = subjects[number - 1]

            except (ValueError, IndexError):

                print("잘못된 번호입니다.")
                continue


            # 해당 과목의 오답 노트 가져오기
            notes = load_notes(subject)


            if not notes:

                print("\n저장된 오답 노트가 없습니다.")
                print("먼저 질문을 하고 오답 노트에 저장해 주세요.")
                continue


            print("\nAI가 오답 노트를 분석해서")
            print("복습 퀴즈를 만들고 있습니다...\n")


            try:

                quiz = make_quiz(notes)

            except Exception as e:

                print("퀴즈를 만드는 중 오류가 발생했습니다.")
                print("오류 내용:", e)
                continue


            if not quiz:

                print("퀴즈를 만들지 못했습니다.")
                continue


            # ======================================
            # 실제 퀴즈 시작
            # ======================================

            score = 0


            print("\n========================================")
            print(f"        {subject} 복습 퀴즈")
            print("========================================")


            for i, question in enumerate(quiz, 1):

                print(f"\n[문제 {i}]")
                print(question["question"])


                print()


                # 보기 출력
                for j, option in enumerate(question["options"], 1):

                    print(f"{j}. {option}")


                # 사용자 답 입력
                while True:

                    try:

                        user_answer = int(
                            input("\n정답 번호 입력 (1~4): ")
                        )


                        if user_answer < 1 or user_answer > 4:

                            print("1~4 중에서 선택해 주세요.")
                            continue


                        break


                    except ValueError:

                        print("숫자를 입력해 주세요.")


                # 정답 확인
                correct_answer = question["answer"]


                if user_answer == correct_answer:

                    print("\n⭕ 정답입니다!")

                    score += 1

                else:

                    print("\n❌ 틀렸습니다.")

                    print(
                        f"정답은 {correct_answer}번입니다."
                    )

                    print(
                        f"정답: "
                        f"{question['options'][correct_answer - 1]}"
                    )


            # ======================================
            # 최종 점수
            # ======================================

            print("\n========================================")
            print("             퀴즈 결과")
            print("========================================")

            print(
                f"{len(quiz)}문제 중 "
                f"{score}문제를 맞혔습니다!"
            )


            percentage = int(
                score / len(quiz) * 100
            )


            print(f"점수: {percentage}점")


            if score == len(quiz):

                print("🎉 모든 문제를 맞혔습니다!")

            elif score >= len(quiz) / 2:

                print("👍 잘했어요! 틀린 문제를 다시 복습해 보세요.")

            else:

                print("📚 오답 노트를 다시 복습해 보는 것을 추천해요.")


        # ==========================================
        # 6. 종료
        # ==========================================

        elif choice == "6":

            print("\nAI 오답 노트 챗봇을 종료합니다.")
            break


        # ==========================================
        # 잘못된 메뉴
        # ==========================================

        else:

            print("\n잘못된 선택입니다.")
            print("1~6 중에서 선택해 주세요.")


# 프로그램 시작
if __name__ == "__main__":

    main()