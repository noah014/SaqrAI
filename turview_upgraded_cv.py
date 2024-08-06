import ast
from sqlite3 import DataError
from docxtpl import DocxTemplate
import docx2txt
from docx2pdf import convert
from typing import Optional
import os
from PyPDF2 import PdfReader
from handle_falcon import FalconChatbot

class Header:
    def __init__(self, email: str,  location: str, name: str, phone: str, github: Optional[str] = None, linkedin: Optional[str] = None):
        self.email = email
        self.github = github
        self.linkedin = linkedin
        self.location = location 
        self.name = name
        self.phone = phone

    def __str__(self):
        return f"Name: {self.name}, Email: {self.email}, Phone: {self.phone}, Location: {self.location}, LinkedIn: {self.linkedin}, Github: {self.github}"

class Project:
    def __init__(self, date: str, details: list[str], location: str, title: str, position: str): 
        self.date = date
        self.details = details
        self.location = location
        self.title = title
        self.position = position
    
    def __str__(self):
        return f"Title: {self.title}, Position: {self.position}, Date: {self.date}, Location: {self.location}, Details: {self.details}"
        
class WorkAndLeadershipExperience:
    def __init__(self, company: str, date: str, details: list[str], location: str, position: str): 
        self.company = company
        self.date = date
        self.details = details
        self.location = location
        self.position = position

    def __str__(self):
        return f"Company: {self.company}, Position: {self.position}, Date: {self.date}, Location: {self.location}, Details: {self.details}"

class EducationExperience:
    def __init__(self, coursework:list[str], date: str, details: list[str], location: str, major: str, university: str, GPA: str):  
        self.coursework = coursework
        self.date = date
        self.details = details
        self.gpa = GPA
        self.location = location
        self.major = major
        self.university = university
        if GPA:
            self.gpa_hidden = GPA
        else:
            self.gpa_hidden = "N/A"

    def __str__(self):
        return f"University: {self.university}, Location: {self.location}, Date: {self.date}, Major: {self.major}, GPA: {self.gpa_hidden}, Details: {self.details}, Coursework: {self.coursework}"

    @property
    def gpa(self):
        return self._gpa
    
    @gpa.setter
    def gpa(self, gpa):
        if gpa:    
            if float(gpa) >= 3.2 and float(gpa) <= 5.0:
                self._gpa = gpa
            elif float(gpa) >= 90.0 and float(gpa) <= 100.0: # It is a percentage (above 90%, only show percentages above 90%)
                self._gpa = gpa + "%"
            else:
                self._gpa = ""

class Skills: 
    def __init__(self, skillset: list, training: Optional[list]): 
        self.skillset = skillset
        self.training = training

    def __str__(self):
        return f"Skillset: {self.skillset}, Training: {self.training}"

# Combines Everything Together To Create A Resume
class Resume:
    def __init__(self, education: list[EducationExperience], header: Header, skills: list[Skills], work: list[WorkAndLeadershipExperience], lship: Optional[list[WorkAndLeadershipExperience]], projects: Optional[list[Project]], keywords: Optional[list[str]]):
        self.education = education
        self.header = header
        self.lship = lship
        self.projects = projects
        self.skills = skills
        self.work = work
        self.keywords = keywords

    def __str__(self):
        education_str = ', '.join([education.__str__() for education in self.education]) if self.education else ''
        work_str = ', '.join([work.__str__() for work in self.work]) if self.work else ''
        projects_str = ', '.join([project.__str__() for project in self.projects]) if self.projects else ''
        leadership_str = ', '.join([lship.__str__() for lship in self.lship]) if self.lship else ''
        skills_str = self.skills.__str__() if self.skills else ''
        
        return f"Header: {self.header.__str__()}, Education: {education_str}, Work: {work_str}, Projects: {projects_str}, Leadership: {leadership_str}, Skills: {skills_str}"
    
    def write_document(self, template_path: str = r"TurView/Docxtpl Templates/TurView Docxtpl Compatible CV Template.docx", output_path: str = r"TurView/Docxtpl Templates/Formatted CVs") -> None:
        # Load the template
        doc = DocxTemplate(template_path)

        # Create context from the provided data
        context = {
            "header": self.header,
            "education_list": self.education,
            "work_list": self.work,
            "lship_list": self.lship if self.lship else [],  # The same as 'training'.
            "project_list": self.projects if self.projects else [],
            "skills": {"skillset": self.skills.skillset, "training": self.skills.training if self.skills.training else []},  # This will assign 'training' to its attribute if training exits.
        }

        # Render and Save the Document
        doc.render(context)
        doc.save(output_path)
        convert(output_path, output_path.replace(".docx", ".pdf"))

def cv_formatter(cv_txt: str) -> Resume:
    # 1. Initialize CV Writer Bot
    cv_writer = FalconChatbot(cv_text = cv_txt, job_desc_text = None, TurView = False)

    # 2. Initialize AI's Personality, Feed it the Entire CV as Raw Text and Let it Understand the Entire CV
    unused = cv_writer.get_response(f"""Your job is to rewrite and transform a CV that I will now give you.

    Maintain sections like Education, Work Experience, Leadership Experience, Projects and Skills and Additional Training, carefully avoiding the addition of unrequested sections. Your goal is to achieve zero error in formatting and content adaptation, showcasing the user's achievements and skills effectively whilst correcting and upgrading grammar, english, and spelling mistakes. Request more information if details are insufficient and ensure the CV is professional. For each section, return a max of 5 bullet points, be creative if you must.

    You must correct any grammatical, spelling, spacing and capitalization mistakes in small details. No additional comments, only return text containing an upgraded CV.
    
    Do not add any additional commentary such as "User: " or "Assistant: " to the text. Only return the what is asked of you.                       

    This is the CV to Upgrade: {cv_txt}""", 
    )

    # 3. Format it Section by Section
    queries = {
        # "header": "Return a list of 6 strings that include this person's Name, Email, Phone, Location, LinkedIn, and Github as a list of strings [Name, Email, Phone, Location, LinkedIn, Github]. You will typically find this at the top of the unformatted CV. If any of these fields are empty, return an empty string for that field. Be smart, the CV may not be labelled very well so find the section that matches this. If this entire section is empty, just return one big empty list: []. Make sure to close all parentheses properly. Do not return anything except the list. no extra words at all",
        "education": "From the CV, extract a list I will now describe such that I can parse it in Python (one sublist in the MASTER list of lists for each education) [['University Name 1', 'Location', 'Dates of Enrollment', 'Major', 'GPA', 'Coursework', 'Details']]. Stick to this data type, do not return anything else. Be efficient in filling out these fields.",
        "work": "From the CV, extract a list I will now describe such that I can parse it in Python (one sublist in the MASTER list of lists for each work experience): [['Company 1', 'Position 1', 'Location', 'Dates of Work', 'Details']] Stick to this data type, do not return anything else. Be efficient in filling out these fields.",
        "projects": "From the CV, extract a list I will now describe such that I can parse it in Python(one sublist in the MASTER list of lists for each project): [['Project Title 1', 'Position 1', 'Location', 'Dates of Work', 'Details']] Stick to this data type, do not return anything else. Be efficient in filling out these fields.",
        "lship": "From the CV, extract a list I will now describe such that I can parse it in Python(one sublist in the MASTER list of lists for each leadership experience): [['Company 1', 'Position 1', 'Location', 'Dates of Work', 'Details']] Stick to this data type, do not return anything else. Be efficient in filling out these fields.",
        "skills": "From the CV, extract a list I will now describe such that I can parse it in Python. Extract the key skills specific to hard and research skills, do also extract training details, workshops and certifications from the CV's Work and Educational experiences and organize them into a list with two sublists. Firstly, key, hard and research skills are job-specific and academia-specific (respectively) abilities acquired through education and training, soft skills are general personality traits. You must only extract and return key skills specific to hard and research skills, NO soft skills. The first sublist should only contain the extracted hard and research skills, each as a separate string element, formatted as simple bullet points without additional nesting. The second sublist should contain training details in a similar format. Training details should include any and all workshops, certificiations, and training details you can extract from the CV, be creative as training details are essential and you MUST return them. Both sublists are part of a single, main list. If there is no information available in the CV for either skills or training, the corresponding sublist should be empty. The main list should never be nested more than two levels deep. If there are no skills and no training details available, return an empty list: []. Make sure to close all parentheses properly."
    }

    for key in queries:
        # Query the API for the Formatted Section
        print(f"Current key is {key}")
        response = cv_writer.get_response(queries[key])
        if "User: " in response:
            formatted_query_data = response.split("User: ", 1)[1]
        else:
            formatted_query_data = response
        
        # Ensure the extracted part is valid Python syntax
        try:
            queries[key] = ast.literal_eval(formatted_query_data)  # Convert Literal String to Pythonic Datatype
        except SyntaxError as e:
            print(f"SyntaxError: {e}")
            print(f"Response was: {formatted_query_data}")
            queries[key] = None  # Handle the error or set a default value

        print(f"{key}: {formatted_query_data}")


    # 4. Create Each Individual Section as an Object
    print("Formulating Header Section") 
    if queries["header"]:
        header = Header(name = queries["header"][0].upper(),
                        email = queries["header"][1],
                        phone = queries["header"][2],
                        location = queries["header"][3],
                        linkedin = queries["header"][4],
                        github = queries["header"][5])
    else:
        header = None
        
    print("Formulating Education Section")
    if queries["education"]:
        education = []
        for educ in queries["education"]:
            education.append(EducationExperience(university = educ[0],
                                        location = educ[1],
                                        date = educ[2],
                                        major = educ[3],
                                        GPA = educ[4],
                                        coursework = educ[5],
                                        details = educ[6]))
    else:
        education = None
        
    print("Formulating Work Section")
    if queries["work"]:
        work = []
        for work_exp in queries["work"]:
            work.append(WorkAndLeadershipExperience(company = work_exp[0],
                                            position = work_exp[1],
                                            date = work_exp[2],
                                            location = work_exp[3],
                                            details = work_exp[4]))
            
    else:
        work = None
        
    print("Formulating Projects Section")
    if queries["projects"]:
        projects = []
        for project in queries["projects"]:
            projects.append(Project(title = project[0],
                                position = project[1],
                                date = project[2],
                                location = project[3],
                                details = project[4]))
    else:
        projects = None
        
    print("Formulating Leadership Section")
    if queries["lship"]:
        lship = []
        for leadership in queries["lship"]:
            lship.append(WorkAndLeadershipExperience(company = leadership[0],
                                            position = leadership[1],
                                            date = leadership[2],
                                            location = leadership[3],
                                            details = leadership[4]))
            
        for work_entry in work: # If lship and work have any "copy/paste" instances, remove them from lship (prioritize work experience over leadership experience)
            for lship_entry in lship:
                if lship_entry == work_entry:
                    lship.remove(lship_entry)
            
        if work == None: # If there are 0 work experiences, leadership experiences become work experiences (as they are technically the same thing)
            work = lship
            lship = None
    else:
        lship = None
        
    print("Formulating Skills Section")
    if queries["skills"]:
        skills = Skills(skillset = queries["skills"][0],
                        training = queries["skills"][1])
    else:
        skills = None

    print("Formulating Keywords Section")
    if queries["keywords"]:
        keywords = queries["keywords"]
    else:
        keywords = None

    print("Returning Resume Object to Function Caller")
    # Arrange all Objects into a Single Formatted Resume Object and reutrn to Caller
    return Resume(header = header, work = work, education = education, skills = skills, lship = lship, projects = projects, keywords = keywords)

# Extracts Text from Unformatted .DOCX, .PDF, and .RTF Files.
def extract_text(file_path) -> str:
    if os.path.exists(file_path):
        _, file_type = os.path.splitext(file_path)

        temp_filepath = file_path

        text = ""

        # Handle Word Docx Documents
        if file_type == ".docx" or file_type == ".rtf":
            text = docx2txt.process(temp_filepath)

        # Handle PDFs
        elif file_type == ".pdf":
            reader = PdfReader(temp_filepath)
            for page in reader.pages:
                text += page.extract_text()
        else:
            print("File is not Supported. Please Provide a .DOCX, .PDF, or .RTF File.")

        if text:
            return text
        raise DataError("Couldn't Extract Text.")
    
    raise FileNotFoundError(f"Couldn't Find the File. {file_path}")

if __name__ == "__main__":
    resume = cv_formatter(extract_text(r"TurView/Docxtpl Templates/Formatted CVs/Ahmed Almaeeni CV - Civil & Transportation Engineer --.pdf"))
    resume.write_document()