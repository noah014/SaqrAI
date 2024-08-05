from docx2pdf import convert
from docxtpl import DocxTemplate

class TurViewReport:
    def __init__(self, name: str, job_desc: str, questions: list[str], ideal_answers: list[str], client_answers: list[str], results: list[(int, str)]):
        self.name = name if name else None
        self.job_desc = job_desc if job_desc else None
        self.questions = Questions(questions)
        self.ideal_answers = Answers(ideal_answers)
        self.client_answers = Answers(client_answers)
        self.results = results if results else None

    def __str___(self):
        return f"""TurView Report for {self.name}

        Job Description: {self.job_desc}

        Questions: {self.questions}

        Ideal Answers: {self.ideal_answers}

        {self.name}'s Answers: {self.client_answers}

        Results: {self.results}
        """
    
    def write_document(self, output_path: str, template_path: str=r"TurView/Docxtpl Templates/TurView Interview Report.docx") -> None:
        # Load the template
        doc = DocxTemplate(template_path)

        # Create context from the provided data
        context = {
            "name": str(self.name) if self.name else [],
            "job_desc": self.job_desc if self.job_desc else [],
            "questions": self.questions if self.questions else [],
            "ideal_answers": self.ideal_answers if self.ideal_answers else [],
            "client_answers": self.client_answers if self.client_answers else [], 
            "results": self.results if self.results else [],
            "maximum_score": max([result[0] for result in self.results]),
            "minimum_score": min([result[0] for result in self.results]),
            "average_score": sum([result[0] for result in self.results]) / len(self.results)
        }

        # Render and Save the Document
        doc.render(context)
        doc.save(output_path)
        convert(output_path, output_path.replace(".docx", ".pdf"))

class Questions:
    def __init__(self, questions: list[str]):
        self.q1 = questions[0] if questions[0] else None
        self.q2 = questions[1] if questions[1] else None
        self.q3 = questions[2] if questions[2] else None
        self.q4 = questions[3] if questions[3] else None
        self.q5 = questions[4] if questions[4] else None

class Answers: 
    def __init__(self, answers: list[str]):
        self.a1 = answers[0] if answers[0] else None
        self.a2 = answers[1] if answers[1] else None
        self.a3 = answers[2] if answers[2] else None
        self.a4 = answers[3] if answers[3] else None
        self.a5 = answers[4] if answers[4] else None

# temp_report = TurViewReport(name="Aditya", job_desc="Software Engineer", questions=["What is your name?", "What is your age?", "What is your name?", "What is your age?", "What is your name?"], ideal_answers=["Aditya", "22", "Aditya", "22", "Aditya"], client_answers=["Aditya", "22", "Aditya", "22", "Aditya"], results=[(5, "Correct"), (6, "Correct"), (5.5, "Correct"), (9, "Correct"), (10, "Correct")])
# temp_report.write_document(r"SaqrAI\TurView\Docxtpl Templates\TurView Interview Report.docx", r"SaqrAI\TurView\Docxtpl Templates\Aditya_report.docx")