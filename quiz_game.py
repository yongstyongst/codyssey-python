
from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.quizzes = [
            Quiz(
                "Python에서 화면에 문자를 출력하는 함수는?",
                ["input()", "print()", "len()", "type()"],
                2
            ),
            Quiz(
                "Git에서 변경 사항을 스테이징하는 명령어는?",
                ["git push", "git pull", "git add", "git log"],
                3
            ),
            Quiz(
                "Docker 컨테이너 목록을 확인하는 명령어는?",
                ["docker ps", "docker build", "docker pull", "docker exec"],
                1
            ),
            Quiz(
                "Python에서 리스트를 만드는 기호는?",
                ["{}", "()", "[]", "<>"],
                3
            ),
            Quiz(
                "Git에서 새로운 브랜치를 생성하고 전환하는 명령어는?",
                ["git status", "git switch -c", "git merge", "git fetch"],
                2
            ),
        ]

        self.best_score = 0

    def play(self):
        score = 0
        total = len(self.quizzes)

        print("\n퀴즈 게임을 시작합니다!")

        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[문제 {index}/{total}]")
            quiz.display()

            while True:
                answer = input("정답 번호 (1-4): ").strip()

                if answer in ("1", "2", "3", "4"):
                    break

                print("1~4 사이의 번호를 입력해 주세요.")

            if quiz.check_answer(int(answer)):
                print("정답입니다!")
                score += 1
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번입니다.")

        percentage = round(score / total * 100)

        print(f"\n최종 점수: {score}/{total} ({percentage}점)")

        if percentage > self.best_score:
            self.best_score = percentage
            print("새로운 최고 점수입니다!")
