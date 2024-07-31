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

def cv_transformer(cv_txt: str) -> Resume:
    cv_format = FalconChatbot(cv_text = cv_txt, job_desc_text = None)

    # 1. Initialize AI's Personality
    cv_format.messages = [
    {"role": "system", "content": """Your job is to rewrite and transform CVs. You will be passed raw text of a CV, your main responsibility is reformulating CVs to maintain the integrity of the original content while making strategic enhancements based on the following requests and return transformed raw text. When adapting Work Experience, Leadership Experience and Projects sections, ensure each contains a minimum of 3 bullet points if there are 3 or more experiences listed. If there are fewer experiences, expand each to at most 5 bullet points to make the CV appear more comprehensive. Your adaptations should prioritize keywords and skills that enhance job market success, emphasizing areas likely to capture an employer's interest. Specifically, for the Skills and Additional Training, mention any skills that are implicitly mentioned, and explicitly state them if they are relevant and can add to the strength of the CV.

    Maintain sections like Education, Work Experience, Leadership Experience, Projects and Skills and Additional Training, carefully avoiding the addition of unrequested sections. Your goal is to achieve zero error in formatting and content adaptation, showcasing the user's achievements and skills effectively. Request more information if details are insufficient and ensure the CV is professional and aligned with the template. Your communication should remain formal, focused on precision and adherence to the provided template.

    If you see any leadership-worthy details as you're transforming, mention this under LEADERSHIP EXPERIENCE with the position of leadership, company of leadership, the date, location, and between 3 and 5 details about it. Look for keywords such as "president", "head", "lead", "captain", "manager", "director", "chief", "coordinator", "supervisor", "organizer", "founder", "chair", "representative". 
     
    If you see any project-worthy details as you're transforming, mention this under PROJECTS with the title of the project, the position held, the date, location, and between 3 and 5 details about it. Look for keywords such as "project", "developed", "created", "built", "designed", "implemented", "launched", "initiated", "established", "organized", "managed".
    
    Remember, feel free to be creative and make the CV as professional as possible.
     
    You must correct any grammatical, spelling, spacing and capitalization mistakes in small details. For example for location, if the raw text says ALAIN or ABUDHABI, you must change this to Al Ain, Abu Dhabi, and so on and so forth. For larger details, if the raw text is unprofessional, upgrade it to a more presentable and professional format.
    """},
    ]

    cv_format.messages.append({"role": "assistant", "content": "Certainly! Please provide the CV you'd like me to transform and I'll augment it to a very professional and high standard."})

    # 2. Get Upgraded CV Back and Feed it to CV Formatter
    formatted_cv_text = cv_format.get_response(cv_txt)

    print(formatted_cv_text)
    return formatted_cv_text

def cv_formatter(cv_txt: str, translate_to_english=True) -> Resume:
    cv_writer = FalconChatbot(cv_text = cv_txt, job_desc_text = None)

    # 1. Initialize AI's Personality
    cv_writer.messages = [
    {"role": "system", "content": """You are a CV-conversion assistant whose job is to take a CV and standardize it in a given format and return it to me in a part-by-part sequential manner. I will pass you an entire CV and you will understand it in whole, then I will pass you the specifics I'd like you to give me which you will professionally paraphrase and return back to me. Don't give me any additional commentary such as "Here is the array", I do not want that, no additional comments as this will break the python script.. Simply pass me the raw array datatype and its contents and I'll handle the rest. Stick to the format I will now specify."""},
    ]
    cv_writer.messages.append({"role": "assistant", "content": "Certainly! Please provide the CV you'd like me to convert, and let me know the specific format or information you want in each part. Once you've shared the CV, you can also specify how you'd like me to organize and present the information and I will stick to it completely."})
    
    # 2. Feed it the Entire CV as Raw Text and Let it Understand the Entire CV
    cv_writer.messages.append({"role": "user", "content": cv_transformer(cv_txt)}) # Call the CV Transformer Function to Extract Data from the CV and Append to Conversation History

    # 3. Format it Section by Section
    queries = {
        "header": "Return a list of 6 strings that include this person's Name, Email, Phone, Location, LinkedIn, and Github as a list of strings [Name, Email, Phone, Location, LinkedIn, Github]. You will typically find this at the top of the unformatted CV. If any of these fields are empty, return an empty string for that field. Be smart, the CV may not be labelled very well so find the section that matches this. If this entire section is empty, just return one big empty list: []. Make sure to close all parentheses properly. Do not return anything except the list. no extra words at all",
        "education": "For each education experience, return each individual education as a sublist of 7 strings that include this person's Univeristy, Location, Date, Major, GPA as a number in  a string format, a sublist of that education Coursework as a list of strings, and a sublist of that education's Details as a list of strings and a sublist as such: [Univeristy, Location, Date, Major, GPA, Coursework, Details]. Absolutely do NOT mention GPA/grade, location, university or date in the details section as these are already mentioned. Try to extract any other relevant details, you must not put GPA or anything else previously mentioned in details. The GPA/grade must be mentioned in the GPA section and don't add any '%' or any labels, you must return the GPA/grade as a number formatted in a string, don't return the GPA as a text grade like good or excellent, it must be a number. For the major section, make sure to mention the major type and major name. For instance, Diploma/Bachelors/Masters/PhD in XYZ. If you can't find a major name, come up with one that is relevant to it, don't leave the 'Major' field empty. For the coursework section, if you can't explicitly extract any relevant coursework, use the major and your knowledge to list common courses that would definitely be taken. If any of these fields are empty, return a an empty string for that field. Be smart, the CV may not be labelled very well so find the section that matches this. Then, put all the sublists in one master list and return them. If this entire section is empty, just return one big empty list: []. For the GPA, just extract the raw number, don't return any text/string data along with it, if the GPA says Very Good/Good/any adjective, just return an empty string. If no location is mentioned, use your knowledge and context clues to come up with city location for the institution. Make sure to close all parentheses properly. Do not return anything except the list. no extra words at all",
        "work": "For their work experience, return each invidiual work experience as a sublist of 5 strings that include this person's Company/organization, Position, Date, Location, and a sublist of the Work Exprience Details (there absolutely MUST be at least 3 details, if you can find more details then mention as many relevant and important ones as you can based on the CV) as a list of strings and a sublist as such: [Company, Position, Date, Location, [Details]]. Absolutely do NOT mention company, position, location or date in the details section as these are already mentioned. Then, put all the sublists in one master list and return them. You will typically find the information needed for this in the Work Experience section of the unformatted CV. Be smart, the CV may not be labelled very well so find the section that matches this. Remember, military service is to be included in education, not in work experience. You might find the Compnay/Organization name inside of the work position, if so add the Company/Organization name as a Company/Organization name. Remember, there absolutely has to be between 3 and 5 detail entries for each work experience. If this entire section is empty, just return one big empty list: []. If no location is mentioned, use your knowledge and context clues to come up with city/country location for the workplace. Make sure to include any sort of experience such as volunteering here as well as regular work experiences. Make sure to close all parentheses properly. Do not return anything except the list. no extra words at all",
        "projects": "For their projects, return each individual project as a sublist of 5 strings that include this person's Title, Position, Date, Location, and a sublist of the Details (there absolutely MUST be at least 3 details, if you can find more details then mention as many relevant and important ones as you can based on the CV) as a list of strings and a sublist as such: [Title, Position, Date, Location, [Details]]. Absolutely do NOT mention title, position, location or date in the details section as these are already mentioned. Then, put all the sublists in one master list and return them. You will typically find the information needed for this in the Projects section of the unformatted CV. Be smart, the CV may not be labelled very well so find the section that matches this. If this entire section is empty, just return one big empty list: []. If no location is mentioned, use your knowledge and context clues to come up with city/country location for the project. Make sure to close all parentheses properly. Do not return anything except the list. no extra words at all",
        "lship": "For their leadership skills/positions, return each leadership position as a sublist of 5 strings that include this person's Company, Position, Date, Location, and a sublist of the Details (there absolutely MUST be at least 3 details, if you can find more details then mention as many relevant and important ones as you can based on the CV) as a list of strings and a sublist as such: [Company, Position, Date, Location, [Details]]. Absolutely do NOT mention company, position, location or date in the details section as these are already mentioned. Do NOT repeat work experience as leadership, make sure there are no identical responses to work experience and leadership experience. Then, put all the sublists in one master list and return them. Look for keywords (specifically in position names) about leadership such as head, chair, leader, lead, manager, president, mentor, coach, etc. Be smart, the CV may not be labelled very well so find the section that matches this. Look for anything related to any degree of leadership from the work experience and education sections as well and extract them here. If this entire section is empty, just return one big empty list: []. If no location is mentioned, use your knowledge and context clues to come up with city/country location for the position. Make sure to close all parentheses properly. Do not return anything except the list. no extra words at all",
        "skills": "Extract the key skills specific to hard and research skills, do also extract training details, workshops and certifications from the CV's Work and Educational experiences and organize them into a list with two sublists. Firstly, key, hard and research skills are job-specific and academia-specific (respectively) abilities acquired through education and training, soft skills are general personality traits. You must only extract and return key skills specific to hard and research skills, NO soft skills. The first sublist should only contain the extracted hard and research skills, each as a separate string element, formatted as simple bullet points without additional nesting. The second sublist should contain training details in a similar format. Training details should include any and all workshops, certificiations, and training details you can extract from the CV, be creative as training details are essential and you MUST return them. Both sublists are part of a single, main list. If there is no information available in the CV for either skills or training, the corresponding sublist should be empty. The main list should never be nested more than two levels deep. If there are no skills and no training details available, return an empty list: []. Make sure to close all parentheses properly. Do not return anything except the list, no extra words at all.",
        "keywords": "Extract the 25 main keywords from this person's CV related ONLY to hard, working skills, positions, and abilities as a list [Keyword1, Keyword2, Keyword3, ...]. These keywords should be extracted from the Work Experience, Leadership Experience, Projects, and Skills sections of the CV. Examples of keywords/phrases include: Engineer, Doctor, AI, AutoCAD, Matlab, Excel, Microsoft Office, ISO Certifications, etc... Make sure to close all parentheses properly and return 25 Keywords, you can be creative."
    }

    for key in queries:
        # Query the API for the Formatted Section
        formatted_query_data = cv_writer.get_response(queries[key])
        queries[key] = ast.literal_eval(formatted_query_data) # Convert Literal String to Pythonic Datatype
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


resume = cv_formatter(extract_text(r"TurView/Docxtpl Templates/Formatted CVs/Ahmed Almaeeni CV - Civil & Transportation Engineer --.pdf"))
resume.write_document()