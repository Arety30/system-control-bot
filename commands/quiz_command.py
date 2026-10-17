from services.quiz_service import QuizService

class QuizCommand:
    def __init__(self):
        self.quiz_service = QuizService()

    def execute(self):
        print("Starting interactive quiz...")
        self.quiz_service.run_quiz()
