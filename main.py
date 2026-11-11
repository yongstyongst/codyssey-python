from quiz_game import QuizGame
def show_menu():
    print("\n" + "=" * 40)
    print("    Python · Git · Docker 기초 퀴즈")
    print("=" * 40)
    print("1. 퀴즈 풀기")
    print("2. 퀴즈 추가")
    print("3. 퀴즈 목록")
    print("4. 점수 확인")
    print("5. 종료")
    print("=" * 40)


def main():
    game = QuizGame()

    try:
        while True:
            show_menu()
            try:
                choice = input("메뉴 선택 (1-5): ").strip()
                if not choice:
                    print("⚠️ 번호를 입력해 주세요.")
                    continue
                try:
                    number = int(choice)
                except ValueError:
                    print("⚠️ 숫자를 입력해 주세요.")
                    continue
                if number == 1:
                    game.play()
                elif number == 2:
                    game.add_quiz()
                elif number == 3:
                    game.list_quizzes()
                elif number == 4:
                    game.show_score()
                elif number == 5:
                    print("👋 퀴즈 게임을 종료합니다.")
                    break
                else:
                    print("⚠️ 1~5 사이의 번호를 입력해 주세요.")
            except (KeyboardInterrupt, EOFError):
                print("\n안전하게 프로그램을 종료합니다.")
                break
    finally:
        if not game.save_state():
            print("⚠️ 종료 시 저장하지 못했습니다. 데이터 파일을 확인해 주세요.")


if __name__ == "__main__":
    main()
