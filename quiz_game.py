
import json
from pathlib import Path
from quiz import Quiz


class QuizGame:
   
    def __init__(self):
        self.state_file = Path(__file__).resolve().parent / "state.json"
        self.quizzes = []
        self.best_score = 0
        self.load_state()
 
    def load_state(self):
        if not self.state_file.exists():
            print("저장 파일이 없습니다. 기본 상태로 시작합니다.")
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("JSON 구조가 올바르지 않습니다.")

            raw_quizzes = data["quizzes"]
            best_score = data["best_score"]

            if not isinstance(raw_quizzes, list):
                raise ValueError("퀴즈 목록 형식이 올바르지 않습니다.")

            if type(best_score) is not int or not 0 <= best_score <= 100:
                raise ValueError("최고 점수 형식이 올바르지 않습니다.")

            loaded_quizzes = [
                Quiz(
                    item["question"],
                    item["choices"],
                    item["answer"]
                )
                for item in raw_quizzes
            ]

            self.quizzes = loaded_quizzes
            self.best_score = best_score

            print(f"저장된 퀴즈 {len(self.quizzes)}개를 불러왔습니다.")

        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"저장 파일을 읽지 못했습니다: {error}")
            print("빈 퀴즈 목록과 기본 점수로 시작합니다.")
 
    def save_state(self):
        data = {
            "quizzes": [
                {
                    "question": quiz.question,
                    "choices": quiz.choices,
                    "answer": quiz.answer
                }
                for quiz in self.quizzes
            ],
            "best_score": self.best_score
        }

        try:
            with self.state_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            print("퀴즈 데이터가 저장되었습니다.")

        except OSError as error:
            print(f"저장 중 오류가 발생했습니다: {error}")

    def add_quiz(self):
        print("\n새로운 퀴즈 추가")

        question = input("문제를 입력하세요: ").strip()

        if not question:
            print("문제 내용은 비워둘 수 없습니다.")
            return

        choices = []

        for number in range(1, 5):
            choice = input(f"{number}번 선택지: ").strip()

            if not choice:
                print("선택지는 비워둘 수 없습니다.")
                return

            choices.append(choice)

        while True:
            answer = input("정답 번호 (1-4): ").strip()

            if answer in ("1", "2", "3", "4"):
                break

            print("1~4 사이의 번호를 입력해 주세요.")

        new_quiz = Quiz(question, choices, int(answer))

        self.quizzes.append(new_quiz)
        self.save_state()

        print("새로운 퀴즈가 추가되었습니다!")
      
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
            self.save_state()
