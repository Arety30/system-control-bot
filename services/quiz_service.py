import json

class QuizService:
    def __init__(self):
        self.questions = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is 2 + 2?", "answer": "4"},
            {"question": "Which language is used for this CLI?", "answer": "Python"}
        ]
        self.score = 0

    def run_quiz(self):
        self.score = 0
        for item in self.questions:
            print(f"Question: {item['question']}")
            user_answer = input("Your answer: ")
            if user_answer.strip().lower() == item['answer'].lower():
                print("Correct!")
                self.score += 1
            else:
                print(f"Wrong. The correct answer was {item['answer']}.")
        print(f"Quiz complete! Your final score: {self.score}/{len(self.questions)}")
        return self.score
