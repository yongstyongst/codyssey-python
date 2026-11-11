
import json
import os
import tempfile
import shutil
from pathlib import Path
from quiz import Quiz
from datetime import datetime
from zoneinfo import ZoneInfo


class QuizGame:
   
    def __init__(self):
        self.state_file = Path(__file__).resolve().parent / "state.json"
        self.backup_file = self.state_file.with_suffix(".json.bak")
        self._load_failed = False
        self.quizzes = []
        self.best_score = 0
        self.history = []
        self.load_state()
 
    def _read_state(self, path):
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("JSON 구조가 올바르지 않습니다.")
        raw_quizzes = data["quizzes"]
        score = data["best_score"]
        if not isinstance(raw_quizzes, list):
            raise ValueError("퀴즈 목록 형식이 올바르지 않습니다.")
        if type(score) is not int or not 0 <= score <= 100:
            raise ValueError("최고 점수 형식이 올바르지 않습니다.")
        quizzes = []
        for item in raw_quizzes:
            question, choices, answer = item["question"], item["choices"], item["answer"]
            if (not isinstance(question, str) or not question.strip()
                    or not isinstance(choices, list) or len(choices) != 4
                    or any(not isinstance(c, str) or not c.strip() for c in choices)
                    or type(answer) is not int):
                raise ValueError("문제 데이터 형식이 올바르지 않습니다.")
            quizzes.append(Quiz(question, choices, answer))
        history = data.get("history", [])

        if not isinstance(history, list):
            raise ValueError("학습 기록 형식이 올바르지 않습니다.")

        return quizzes, score, history

    def _atomic_copy(self, source, destination):
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=destination.parent, prefix=".quiz-",
                suffix=".tmp", delete=False
            ) as file:
                temporary = Path(file.name)
                with source.open("rb") as original:
                    shutil.copyfileobj(original, file)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def load_state(self):
        self._load_failed = False
        if not self.state_file.exists() and not self.backup_file.exists():
            print("저장 파일이 없습니다. 기본 상태로 시작합니다.")
            return

        errors = (OSError, ValueError, KeyError, TypeError, UnicodeError)
        if self.state_file.exists():
            try:
                self.quizzes, self.best_score, self.history = self._read_state(self.state_file)
                print(f"저장된 퀴즈 {len(self.quizzes)}개를 불러왔습니다.")
                return
            except errors as error:
                print(f"저장 파일을 읽지 못했습니다: {error}")

        if self.backup_file.exists():
            try:
                quizzes, score, history = self._read_state(self.backup_file)
                self._atomic_copy(self.backup_file, self.state_file)
                self.quizzes, self.best_score = quizzes, score
                self.history = history
                print(f"백업에서 퀴즈 {len(quizzes)}개를 복원했습니다.")
                return
            except errors as error:
                print(f"백업 파일을 복원하지 못했습니다: {error}")

        self._load_failed = True
        print("복구할 수 없어 저장이 잠겼습니다. 원본 파일을 확인해 주세요.")

    def save_state(self):
        if self._load_failed:
            print("⚠️ 손상된 저장 파일 보호를 위해 덮어쓰지 않습니다.")
            return False

        data = {
            "quizzes": [
                {"question": q.question, "choices": q.choices, "answer": q.answer}
                for q in self.quizzes
            ],
            "best_score": self.best_score,
            "history": self.history,
        }
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.state_file.parent,
                prefix=".quiz-", suffix=".tmp", delete=False
            ) as file:
                temporary = Path(file.name)
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            # 백업을 먼저 갱신하여 원본 교체 실패에도 복구본을 보존합니다.
            self._atomic_copy(temporary, self.backup_file)
            os.replace(temporary, self.state_file)
            print("퀴즈 데이터와 백업이 저장되었습니다.")
            return True
        except (OSError, ValueError, TypeError) as error:
            print(f"저장 중 오류가 발생했습니다: {error}")
            return False
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

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

    def list_quizzes(self):
        print("\n========== 퀴즈 목록 ==========")

        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        print(f"전체 퀴즈: {len(self.quizzes)}개")

        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"\n[퀴즈 {index}]")
            quiz.display()
            print(f"정답: {quiz.answer}번")

        print("\n===============================")

    def show_score(self):
        print("\n========== 점수 확인 ==========")
        print(f"현재 최고 점수: {self.best_score}점")
        print(f"등록된 퀴즈 수: {len(self.quizzes)}개")
        print("===============================")
      
    def play(self):
        score = 0
        total = len(self.quizzes)
        
        if total == 0:
            print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return
        
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

        record = {
            "date": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "correct": score,
            "score": percentage
        }

        self.history.append(record)

        if self.save_state():
            print("학습 기록이 저장되었습니다.")


    def show_history(self):
        print("\n========== 학습 기록 ==========")

        if not self.history:
            print("저장된 학습 기록이 없습니다.")
            return

        for index, record in enumerate(self.history, start=1):
            print(
                f"{index}회차 | {record['date']} | "
                f"{record['total']}문제 | "
                f"{record['correct']}개 정답 | "
                f"{record['score']}점"
            )

        print(f"\n총 응시 횟수: {len(self.history)}회")
        print(f"최고 점수: {self.best_score}점")
        print("================================")
