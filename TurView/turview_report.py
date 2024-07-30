from docx2pdf import convert
from docxtpl import DocxTemplate

class TurViewReport:
    def __init__(self, name: str, questions: list[str], ideal_answers: list[str], client_answers: list[str], results: list[(int, str)]):
        pass
    
    def write_document(self, template_path: str, output_path: str) -> None:
        # Load the template
        doc = DocxTemplate(template_path)

        # Create context from the provided data
        context = {}

        # Render and Save the Document
        doc.render(context)
        doc.save(output_path)
        convert(output_path, output_path.replace(".docx", ".pdf"))

