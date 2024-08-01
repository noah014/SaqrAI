from docx2pdf import convert
from docxtpl import DocxTemplate

class TurViewReport:
    def __init__(self, name: str, job_desc: str, questions: list[str], ideal_answers: list[str], client_answers: list[str], results: list[(int, str)]):
        pass
    
    def write_document(self, template_path: str, output_path: str) -> None:
        # Load the template
        doc = DocxTemplate(template_path)

        # Create context from the provided data
        context = {
            "name": self.name if self.name else None,
            "job_desc": self.job_desc if self.job_desc else None,
            "questions": self.questions if self.questions else None,
            "ideal_answers": self.ideal_answers if self.ideal_answers else None,
            "client_answers": self.client_answers if self.client_answers else None, 
            "results": self.results if self.results else None,
            "maximum_score": max([result[0] for result in self.results]),
            "minimum_score": min([result[0] for result in self.results]),
            "average_score": sum([result[0] for result in self.results]) / len(self.results)
        }

        # Render and Save the Document
        doc.render(context)
        doc.save(output_path)
        convert(output_path, output_path.replace(".docx", ".pdf"))

