from ai71 import AI71 

AI71_API_KEY = "api71-api-cbdf95af-ec38-4f97-8d7e-cb2ec3823f46"

for chunk in AI71(AI71_API_KEY).chat.completions.create(
    model="tiiuae/falcon-180b-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant who will come up with 10 interview questions based on a CV and a job description. 8 questions should be behavioral, and 2 questions should be technical."},
        {"role": "user", "content": """This is the CV: SULTAN WALEED ALHOSANI
alhosani909@gmail.com | +971 56 757 7346 | Abu Dhabi, UAE
EDUCATION 
ADNOC Technical Academy Abu Dhabi, UAE
Diploma in Process Operation 2021
• Coursework: Common Core, Petroleum Core, Specialization Core, OJT, H2S Awareness Escape — Level 2
Sa’ad Bin Mo’ath School Abu Dhabi, UAE
Secondary School Certificate 2015
• GPA: 95.7%
WORK EXPERIENCE 
ADNOC Technical Academy Abu Dhabi, UAE
Start-up and Shutdown Supervisor 2018–2019
• Supervised start-up and shutdown processes for four plants, ensuring adherence to all safety procedures.
• Managed operations at the Wellhead.
• Operated the Oil Plant.
• Handled the Gas Dehydration Unit.
• Controlled the Gas Sweetening Unit.
Olympics World Summer Games Abu Dhabi, UAE
Participant March 2019
• Actively engaged in various competitions, enhancing team-building and discipline skills.
• Demonstrated commitment and enthusiasm in representing the institution.
• Gained experience in international sporting events.
SKILLS AND ADDITIONAL TRAINING 
1. Supervised start-up and shutdown processes
2. Managed operations at the Wellhead
3. Operated the Oil Plant
4. Handled the Gas Dehydration Unit
5. Controlled the Gas Sweetening Unit
6. Executed PIGGING operations, including both Receiver and Launcher
7. Conducted choke changes successfully
• H2S Awareness Escape — Level 2
• PET Certificate Level B1 
         
Job Description:
         Job Title: Process Operations Supervisor

Location: Abu Dhabi, UAE

Company: Al Noor Energy Solutions

About the Company:
Al Noor Energy Solutions is a leading provider of innovative energy solutions specializing in the oil and gas industry. Our commitment to safety, efficiency, and sustainability drives our operations, and we pride ourselves on delivering top-notch services to our clients.

Job Description:

Overview:
Al Noor Energy Solutions is seeking a highly skilled and experienced Process Operations Supervisor to oversee and manage the start-up and shutdown processes of our plants. The ideal candidate will have a strong background in process operations, particularly within the oil and gas industry, and demonstrate a commitment to safety and efficiency.

Key Responsibilities:

Supervise the start-up and shutdown processes for multiple plants, ensuring strict adherence to safety protocols and procedures.
Manage operations at the wellhead, including monitoring and controlling equipment to maintain optimal performance.
Operate and oversee the Oil Plant, Gas Dehydration Unit, and Gas Sweetening Unit to ensure seamless and efficient operations.
Execute PIGGING operations, including both Receiver and Launcher, to maintain pipeline integrity and flow efficiency.
Conduct choke changes and manage pressure control devices to optimize production rates and ensure safety.
Coordinate with the maintenance team to schedule and perform regular inspections and preventive maintenance on all operational equipment.
Develop and implement operational procedures and guidelines to enhance efficiency and safety in all processes.
Provide training and guidance to junior staff and ensure compliance with all health, safety, and environmental regulations.
Participate in safety drills and H2S awareness programs to maintain a high level of preparedness among all team members.
Qualifications:

Diploma in Process Operation or a related field.
Minimum of 3 years of experience in process operations within the oil and gas industry.
Proven experience in supervising start-up and shutdown processes.
Strong knowledge of wellhead operations, oil plant operations, gas dehydration, and gas sweetening.
Proficiency in executing PIGGING operations and conducting choke changes.
Certification in H2S Awareness Escape — Level 2.
Excellent problem-solving skills and the ability to make sound decisions under pressure.
Strong communication and leadership skills.
Skills:

Supervision of start-up and shutdown processes
Wellhead operations management
Oil plant operation
Gas dehydration unit operation
Gas sweetening unit operation
PIGGING operations (Receiver and Launcher)
Choke changes
H2S Awareness Escape — Level 2
PET Certificate Level B1
Additional Information:

Competitive salary and benefits package.
Opportunities for career advancement and professional development.
Collaborative and dynamic work environment."""},
    ],
    stream=True,
):
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, sep="", end="", flush=True)

