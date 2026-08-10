import csv
import os
import random
from datetime import datetime, timedelta

# Create raw directory if it doesn't exist
os.makedirs("data/raw", exist_ok=True)

# Common Indian names for Jamshedpur context
FIRST_NAMES = [
    "Aarav", "Amit", "Aniket", "Arjun", "Ashok", "Dev", "Ganesh", "Hari", "Jay", "Karan",
    "Madhav", "Nikhil", "Pranav", "Rajesh", "Sanjay", "Vijay", "Yash", "Ananya", "Deepa",
    "Jyoti", "Kiran", "Meera", "Neha", "Pooja", "Ritu", "Sita", "Sunita", "Tanvi", "Aditya",
    "Bhaskar", "Chandan", "Dinesh", "Gopal", "Hemant", "Jagdish", "Kailash", "Manish", "Narendra",
    "Pankaj", "Ramesh", "Suresh", "Vikram", "Abhishek", "Rohan", "Rahul", "Sandeep", "Alok"
]
LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Kumar", "Gupta", "Patel", "Mehta", "Joshi", "Das", "Sen",
    "Rao", "Nair", "Reddy", "Choudhury", "Mishra", "Pandey", "Dubey", "Yadav", "Prasad", "Sinha",
    "Banerjee", "Chatterjee", "Mukherjee", "Roy", "Bose", "Dutta", "Mitra", "Ghosh", "Tripathi"
]

def generate_random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

# 1. Departments (10 departments)
DEPARTMENTS = [
    {"id": 1, "name": "Mechanical Maintenance", "code": "MECH", "description": "Responsible for mechanical plant maintenance, piping, and equipment reliability.", "head_name": "Rajesh Verma", "location": "Jamshedpur Plant", "is_active": "True"},
    {"id": 2, "name": "Electrical & Electronics", "code": "ELEC", "description": "Handles electrical grids, motors, sub-stations, and instrumentation.", "head_name": "Sanjay Sen", "location": "Jamshedpur Plant", "is_active": "True"},
    {"id": 3, "name": "Automation & Control", "code": "AUTO", "description": "PLC systems, SCADA networks, and automated rolling mill controls.", "head_name": "Amit Patel", "location": "Jamshedpur Plant", "is_active": "True"},
    {"id": 4, "name": "Blast Furnace Operations", "code": "BF", "description": "Ironmaking operations, raw material charging, and hot metal tapping.", "head_name": "Vijay Prasad", "location": "Jamshedpur Plant", "is_active": "True"},
    {"id": 5, "name": "Rolling Mill Operations", "code": "RM", "description": "Hot and cold rolling operations for sheets, wires, and structural steels.", "head_name": "Karan Mishra", "location": "Jamshedpur Plant", "is_active": "True"},
    {"id": 6, "name": "Quality Assurance & Metallurgy", "code": "QA", "description": "Chemical composition verification, tensile testing, and quality certification.", "head_name": "Meera Joshi", "location": "Jamshedpur Plant", "is_active": "True"},
    {"id": 7, "name": "Supply Chain & SCM", "code": "SCM", "description": "Logistics, raw material imports, and finished steel distribution.", "head_name": "Ananya Roy", "location": "Plant HQ", "is_active": "True"},
    {"id": 8, "name": "Information Technology", "code": "IT", "description": "Enterprise software support, SAP systems, and networking infrastructure.", "head_name": "Nikhil Bose", "location": "Plant HQ", "is_active": "True"},
    {"id": 9, "name": "AI & Digital Initiatives", "code": "AI", "description": "Predictive modeling, computer vision for safety, and digital twin implementations.", "head_name": "Pranav Gupta", "location": "Plant HQ", "is_active": "True"},
    {"id": 10, "name": "Human Resources & L&D", "code": "HR", "description": "Talent acquisition, employee self-service portal, training catalog management.", "head_name": "James Okonkwo", "location": "Plant HQ", "is_active": "True"}
]

# Write departments.csv
with open("data/raw/departments.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "code", "description", "head_name", "location", "is_active"])
    writer.writeheader()
    writer.writerows(DEPARTMENTS)

# 2. Job Roles (50 roles)
ROLES = [
    # Mechanical Maintenance (7 roles)
    {"id": 1, "title": "Technician - Mechanical", "department_id": 1, "grade": 2, "track": "Technical", "min_experience_years": 0, "description": "Performs basic maintenance and repairs of mechanical systems.", "preferred_certifications": "ITI Mechanical", "is_active": "True"},
    {"id": 2, "title": "Senior Technician - Mechanical", "department_id": 1, "grade": 3, "track": "Technical", "min_experience_years": 3, "description": "Performs complex mechanical maintenance, diagnostics, and repairs.", "preferred_certifications": "ITI Mechanical, Safety Certification", "is_active": "True"},
    {"id": 3, "title": "Mechanical Engineer", "department_id": 1, "grade": 5, "track": "Technical", "min_experience_years": 2, "description": "Coordinates maintenance schedules, plans shutdowns, and executes reliability projects.", "preferred_certifications": "B.Tech Mechanical Engineering", "is_active": "True"},
    {"id": 4, "title": "Senior Mechanical Engineer", "department_id": 1, "grade": 6, "track": "Technical", "min_experience_years": 6, "description": "Designs complex mechanical system modifications, manages engineering projects.", "preferred_certifications": "B.Tech Mechanical Engineering, Project Management", "is_active": "True"},
    {"id": 5, "title": "Mechanical Specialist", "department_id": 1, "grade": 7, "track": "Technical", "min_experience_years": 10, "description": "Domain expert in mechanical systems, vibration analysis, and failure diagnostics.", "preferred_certifications": "M.Tech Mechanical Engineering, Vibration Analyst Level II", "is_active": "True"},
    {"id": 6, "title": "EAF Mechanical Specialist", "department_id": 1, "grade": 7, "track": "Technical", "min_experience_years": 8, "description": "Domain expert in Electric Arc Furnace (EAF) mechanical operations, electrode columns, and hydraulics.", "preferred_certifications": "B.Tech Mechanical, EAF Safety and Design", "is_active": "True"},
    {"id": 7, "title": "Engineering Manager", "department_id": 1, "grade": 8, "track": "Leadership", "min_experience_years": 8, "description": "Manages mechanical maintenance teams, shutdown budgets, and asset reliability.", "preferred_certifications": "B.Tech Mechanical + MBA", "is_active": "True"},
]

# Generate rest of the roles programmatically to reach 50
role_id_counter = 8
titles = ["Technician", "Senior Technician", "Engineer", "Senior Engineer", "Specialist", "Manager", "Head"]
for dept in DEPARTMENTS[1:]:  # From Electrical onwards
    dept_id = dept["id"]
    dept_name = dept["name"]
    for i, title in enumerate(titles):
        track = "Leadership" if title in ["Manager", "Head"] else "Technical"
        ROLES.append({
            "id": role_id_counter,
            "title": f"{title} - {dept_name}" if title != "Head" else f"Head - {dept_name}",
            "department_id": dept_id,
            "grade": i + 2,
            "track": track,
            "min_experience_years": i * 2,
            "description": f"Responsible for {title.lower()} tasks in {dept_name}.",
            "preferred_certifications": f"Degree/Diploma in relevant field",
            "is_active": "True"
        })
        role_id_counter += 1

# Ensure Gareth, Priya and James roles exist
# Gareth: Mechanical Engineer (Role 3), Priya: Engineering Manager (Role 7), James: HR Head/Specialist (let's check James' title)
# James Okonkwo: HR Business Partner (grade 7). Let's check what role James Okonkwo has. In AuthContext, it was "HR Business Partner"
# We can overwrite or add it specifically
ROLES.append({
    "id": role_id_counter,
    "title": "HR Business Partner",
    "department_id": 10,
    "grade": 7,
    "track": "Leadership",
    "min_experience_years": 6,
    "description": "Aligns business objectives with employees and management in designated business units.",
    "preferred_certifications": "MBA HR",
    "is_active": "True"
})
role_id_counter += 1

# Write job_roles.csv
with open("data/raw/job_roles.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "title", "department_id", "grade", "track", "min_experience_years", "description", "preferred_certifications", "is_active"])
    writer.writeheader()
    writer.writerows(ROLES)

# 3. Skills (200 skills)
SKILLS = []
categories = ["Technical", "Safety", "Leadership", "Digital", "Behavioral"]
subcategories = {
    "Technical": ["Metallurgy", "Maintenance", "Ironmaking", "Design", "Automation", "Instrumentation"],
    "Safety": ["Industrial Safety", "Hazard Management", "Compliance"],
    "Leadership": ["Team Operations", "Strategic Planning", "Project Management"],
    "Digital": ["Software", "Data Science", "IIoT", "Advanced Technologies"],
    "Behavioral": ["Communication", "Problem Solving", "Collaboration"]
}

# Add some specific skills for EAF and Mechanical Maintenance
SPECIFIC_SKILLS = [
    ("Mechanical Systems", "Technical", "Maintenance"),
    ("EAF Operations", "Technical", "Ironmaking"),
    ("Maintenance", "Technical", "Maintenance"),
    ("Predictive Maintenance", "Technical", "Maintenance"),
    ("Root Cause Analysis", "Technical", "Problem Solving"),
    ("Equipment Reliability", "Technical", "Maintenance"),
    ("Hydraulics", "Technical", "Maintenance"),
    ("Industrial Safety", "Safety", "Industrial Safety"),
    ("Electrical Systems", "Technical", "Instrumentation"),
    ("Condition Monitoring", "Technical", "Maintenance"),
    ("PLC Programming", "Technical", "Automation"),
    ("SCADA", "Technical", "Automation"),
    ("Python", "Digital", "Software"),
    ("Machine Learning", "Digital", "Data Science"),
    ("Data Analysis", "Digital", "Data Science"),
    ("SAP ERP", "Digital", "Software"),
    ("LOTO", "Safety", "Industrial Safety"),
    ("Confined Space", "Safety", "Industrial Safety")
]

skill_id = 1
for name, cat, sub in SPECIFIC_SKILLS:
    SKILLS.append({
        "id": skill_id,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "description": f"Expertise in {name.lower()}.",
        "future_demand": random.choice(["Medium", "High", "Critical"]),
        "criticality": random.choice(["Medium", "High", "Critical"]),
        "is_active": "True"
    })
    skill_id += 1

# Generate remaining to reach 200
while len(SKILLS) < 200:
    cat = random.choice(categories)
    sub = random.choice(subcategories[cat])
    name = f"{cat} skill - {sub} {skill_id}"
    SKILLS.append({
        "id": skill_id,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "description": f"Description of {name}.",
        "future_demand": random.choice(["Low", "Medium", "High"]),
        "criticality": random.choice(["Low", "Medium", "High", "Critical"]),
        "is_active": "True"
    })
    skill_id += 1

# Write skills.csv
with open("data/raw/skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "subcategory", "description", "future_demand", "criticality", "is_active"])
    writer.writeheader()
    writer.writerows(SKILLS)

# 4. Training Courses (100 courses)
COURSES = []
course_id = 1

# Specific courses mapped to critical skills
SPECIFIC_COURSES = [
    ("Predictive Maintenance Fundamentals", "Technical", "Maintenance", 16, "Predictive Maintenance"),
    ("Condition Monitoring", "Technical", "Maintenance", 24, "Condition Monitoring"),
    ("Advanced Predictive Maintenance", "Technical", "Maintenance", 40, "Predictive Maintenance"),
    ("EAF Design & Process Optimization", "Technical", "Ironmaking", 40, "EAF Operations"),
    ("EAF Operations Safety", "Safety", "Industrial Safety", 8, "EAF Operations,Industrial Safety"),
    ("Mechanical Systems Maintenance", "Technical", "Maintenance", 16, "Mechanical Systems,Maintenance"),
    ("Industrial Hydraulics & Pneumatics", "Technical", "Maintenance", 32, "Hydraulics"),
    ("Industrial Safety Standards", "Safety", "Industrial Safety", 8, "Industrial Safety"),
    ("Lock-Out Tag-Out (LOTO) Procedures", "Safety", "Industrial Safety", 4, "LOTO,Industrial Safety"),
    ("Root Cause Analysis (RCA) Methodology", "Behavioral", "Problem Solving", 16, "Root Cause Analysis"),
    ("PLC Programming for Automation", "Technical", "Automation", 40, "PLC Programming"),
    ("Python for Data Analytics", "Digital", "Software", 32, "Python,Data Analysis"),
    ("Introduction to Machine Learning", "Digital", "Data Science", 40, "Machine Learning"),
]

for name, cat, sub, dur, skills in SPECIFIC_COURSES:
    COURSES.append({
        "id": course_id,
        "code": f"CRS{1000 + course_id}",
        "name": name,
        "description": f"Comprehensive course on {name}.",
        "category": cat,
        "subcategory": sub,
        "duration_hours": dur,
        "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
        "mode": random.choice(["Online", "Classroom", "Blended"]),
        "provider": random.choice(["Tata Steel Digie-Shala", "Internal Academy", "OEM"]),
        "skills_covered": skills,
        "prerequisites": "",
        "target_grades": "3,4,5,6,7,8",
        "is_mandatory": "True" if "Safety" in name or "EAF" in name else "False",
        "pass_score": 75,
        "is_active": "True"
    })
    course_id += 1

# Generate remaining to reach 100
while len(COURSES) < 100:
    cat = random.choice(categories)
    sub = random.choice(subcategories[cat])
    name = f"General Course on {cat} - {sub} {course_id}"
    skills_list = random.sample([s["name"] for s in SKILLS if s["category"] == cat], min(2, 5))
    COURSES.append({
        "id": course_id,
        "code": f"CRS{1000 + course_id}",
        "name": name,
        "description": f"Details for {name}.",
        "category": cat,
        "subcategory": sub,
        "duration_hours": random.choice([4, 8, 16, 24, 40]),
        "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
        "mode": random.choice(["Online", "Classroom", "Blended"]),
        "provider": "Internal Training Academy",
        "skills_covered": ",".join(skills_list),
        "prerequisites": "",
        "target_grades": "1,2,3,4,5,6,7,8",
        "is_mandatory": "False",
        "pass_score": 70,
        "is_active": "True"
    })
    course_id += 1

# Write training_courses.csv
with open("data/raw/training_courses.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "code", "name", "description", "category", "subcategory", "duration_hours", "difficulty", "mode", "provider", "skills_covered", "prerequisites", "target_grades", "is_mandatory", "pass_score", "is_active"])
    writer.writeheader()
    writer.writerows(COURSES)

# 5. Employees (~500 employees)
EMPLOYEES = []

# Mock users presets
# 1. Gareth Williams
# 2. Priya Sharma
# 3. James Okonkwo

# Find matching role ids
role_mech_eng_id = [r["id"] for r in ROLES if r["title"] == "Mechanical Engineer" and r["department_id"] == 1][0]
role_mech_mgr_id = [r["id"] for r in ROLES if r["title"] == "Engineering Manager" and r["department_id"] == 1][0]
role_hr_bp_id = [r["id"] for r in ROLES if r["title"] == "HR Business Partner" and r["department_id"] == 10][0]

MOCK_EMPS = [
    {"id": 1, "employee_number": "EMP1000", "data_source": "SYNTHETIC_DEMO", "name": "Gareth Williams", "email": "gareth.williams@steelcore.com", "department_id": 1, "role_id": role_mech_eng_id, "manager_id": 2, "grade": 5, "years_experience": 4.5, "years_in_company": 3.0, "location": "Jamshedpur Plant", "employment_status": "Active", "performance_rating": "Meets Expectations", "last_rating_score": 3.0, "phone": "+91-9876543210", "is_active": "True"},
    {"id": 2, "employee_number": "EMP1001", "data_source": "SYNTHETIC_DEMO", "name": "Priya Sharma", "email": "priya.sharma@steelcore.com", "department_id": 1, "role_id": role_mech_mgr_id, "manager_id": 4, "grade": 8, "years_experience": 12.0, "years_in_company": 8.0, "location": "Jamshedpur Plant", "employment_status": "Active", "performance_rating": "Exceeds Expectations", "last_rating_score": 4.0, "phone": "+91-9876543211", "is_active": "True"},
    {"id": 3, "employee_number": "EMP1002", "data_source": "SYNTHETIC_DEMO", "name": "James Okonkwo", "email": "james.okonkwo@steelcore.com", "department_id": 10, "role_id": role_hr_bp_id, "manager_id": 5, "grade": 7, "years_experience": 9.0, "years_in_company": 5.0, "location": "Plant HQ", "employment_status": "Active", "performance_rating": "Meets Expectations", "last_rating_score": 3.0, "phone": "+91-9876543212", "is_active": "True"}
]

for emp in MOCK_EMPS:
    EMPLOYEES.append(emp)

# Generate rest of the employees to reach 500
emp_id = 4
while len(EMPLOYEES) < 500:
    dept = random.choice(DEPARTMENTS)
    dept_roles = [r for r in ROLES if r["department_id"] == dept["id"]]
    role = random.choice(dept_roles)
    
    rating = random.choice(["Meets Expectations", "Exceeds Expectations", "Exceptional", "Partially Meets Expectations"])
    score_map = {
        "Exceptional": 5.0,
        "Exceeds Expectations": 4.0,
        "Meets Expectations": 3.0,
        "Partially Meets Expectations": 2.0
    }
    
    EMPLOYEES.append({
        "id": emp_id,
        "employee_number": f"EMP{1000 + emp_id - 1}",
        "data_source": "SYNTHETIC_DEMO",
        "name": generate_random_name(),
        "email": f"emp{1000 + emp_id - 1}@tatasteel.mock",
        "department_id": dept["id"],
        "role_id": role["id"],
        "manager_id": "", # Will resolve manager links in the import script
        "grade": role["grade"],
        "years_experience": round(random.uniform(role["min_experience_years"], role["min_experience_years"] + 15), 1),
        "years_in_company": round(random.uniform(0.5, 12.0), 1),
        "location": dept["location"],
        "employment_status": "Active",
        "performance_rating": rating,
        "last_rating_score": score_map[rating],
        "phone": f"+91-912345{emp_id:04d}",
        "is_active": "True"
    })
    emp_id += 1

# Write employees.csv
with open("data/raw/employees.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_number", "data_source", "name", "email", "department_id", "role_id", "manager_id", "grade", "years_experience", "years_in_company", "location", "employment_status", "performance_rating", "last_rating_score", "phone", "is_active"])
    writer.writeheader()
    writer.writerows(EMPLOYEES)

# 6. Employee Skills (~3000 relationships)
# Make sure employees have realistic skills based on their department
EMP_SKILLS = []
emp_skill_id = 1

# Pre-assign Gareth Williams specific skills
# Gareth has "Mechanical Systems", "Maintenance", "Predictive Maintenance", "Root Cause Analysis", "Equipment Reliability", "Industrial Safety"
gareth_skills = [
    ("Mechanical Systems", "Advanced"),
    ("Maintenance", "Advanced"),
    ("Predictive Maintenance", "Intermediate"),
    ("Root Cause Analysis", "Intermediate"),
    ("Equipment Reliability", "Intermediate"),
    ("Industrial Safety", "Advanced"),
]

for s_name, lvl in gareth_skills:
    s_id = [s["id"] for s in SKILLS if s["name"] == s_name][0]
    EMP_SKILLS.append({
        "id": emp_skill_id,
        "employee_id": 1,
        "skill_id": s_id,
        "level": lvl,
        "years_experience": 3.5,
        "is_certified": "True",
        "certification_name": "Tata Steel Core Safety Certification",
        "last_assessed": (datetime.utcnow() - timedelta(days=random.randint(10, 180))).isoformat(),
        "notes": "Verified through department annual appraisal."
    })
    emp_skill_id += 1

# Generate remaining to reach 3000 relationships
# Associate skills with employees of relevant departments
# e.g., MECH employees should have MECH/Technical/Safety skills
for emp in EMPLOYEES:
    emp_id = emp["id"]
    dept_id = emp["department_id"]
    
    # Select category priority
    if dept_id in [1, 2, 3, 4, 5, 6]:
        primary_cat = "Technical"
    elif dept_id in [8, 9]:
        primary_cat = "Digital"
    else:
        primary_cat = "Behavioral"
        
    skills_in_pool = [s for s in SKILLS if s["category"] in [primary_cat, "Safety", "Behavioral"]]
    emp_chosen_skills = random.sample(skills_in_pool, min(len(skills_in_pool), random.randint(5, 10)))
    
    for sk in emp_chosen_skills:
        # Avoid duplicating Gareth's skills
        if emp_id == 1 and any(es["skill_id"] == sk["id"] for es in EMP_SKILLS if es["employee_id"] == 1):
            continue
            
        EMP_SKILLS.append({
            "id": emp_skill_id,
            "employee_id": emp_id,
            "skill_id": sk["id"],
            "level": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
            "years_experience": round(random.uniform(0.5, 8.0), 1),
            "is_certified": "True" if random.random() > 0.6 else "False",
            "certification_name": "Internal Training Course Certification" if random.random() > 0.6 else "",
            "last_assessed": (datetime.utcnow() - timedelta(days=random.randint(10, 360))).isoformat(),
            "notes": ""
        })
        emp_skill_id += 1

# Limit to ~3000 relationships
EMP_SKILLS = EMP_SKILLS[:3000]

# Write employee_skills.csv
with open("data/raw/employee_skills.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "skill_id", "level", "years_experience", "is_certified", "certification_name", "last_assessed", "notes"])
    writer.writeheader()
    writer.writerows(EMP_SKILLS)

# 7. Employee Training Records (~3000 records)
EMP_TRAINING = []
emp_training_id = 1

# Pre-assign Gareth's records
# Gareth has 1 record for Mandatory static attitude Course (id 8/expired in the previous database setup, but let's map it cleanly)
# We can map it to "EAF Operations Safety" which has id 5 and target course code CRS1005 (or similar).
# Let's map Gareth to have completed "Mechanical Systems Maintenance" and "Lock-Out Tag-Out (LOTO) Procedures", 
# and have "EAF Operations Safety" as Expired.
gareth_trainings = [
    {"course_id": 6, "status": "Completed", "score": 85.0, "comp_days": 120, "exp_days": -180, "hours": 16.0}, # Completed Mechanical Systems Maintenance
    {"course_id": 9, "status": "Completed", "score": 90.0, "comp_days": 90, "exp_days": -180, "hours": 4.0},   # Completed Lock-Out Tag-Out
    {"course_id": 5, "status": "Expired", "score": 78.0, "comp_days": 380, "exp_days": -20, "hours": 8.0}    # Expired EAF Operations Safety
]

for t in gareth_trainings:
    comp_date = datetime.utcnow() - timedelta(days=t["comp_days"])
    exp_date = comp_date + timedelta(days=365) if t["status"] in ["Completed", "Expired"] else None
    
    EMP_TRAINING.append({
        "id": emp_training_id,
        "employee_id": 1,
        "course_id": t["course_id"],
        "status": t["status"],
        "score": t["score"] if t["status"] in ["Completed", "Expired"] else "",
        "completion_date": comp_date.isoformat() if t["status"] in ["Completed", "Expired"] else "",
        "expiry_date": exp_date.isoformat() if exp_date else "",
        "hours_completed": t["hours"],
        "certificate_issued": "True" if t["status"] == "Completed" else "False",
        "notes": ""
    })
    emp_training_id += 1

# Generate remaining to reach 3000 training records
for emp in EMPLOYEES:
    emp_id = emp["id"]
    if emp_id == 1:
        continue # Skip Gareth since already seeded
        
    num_courses = random.randint(4, 8)
    chosen_courses = random.sample(COURSES, num_courses)
    
    for c in chosen_courses:
        status = random.choice(["Completed", "In Progress", "Not Started", "Expired"])
        comp_date = datetime.utcnow() - timedelta(days=random.randint(10, 500)) if status in ["Completed", "Expired"] else None
        exp_date = comp_date + timedelta(days=365) if status == "Completed" else (comp_date - timedelta(days=10) if status == "Expired" else None)
        
        hours = c["duration_hours"] if status == "Completed" else (random.uniform(0.5, c["duration_hours"]) if status == "In Progress" else 0.0)
        
        EMP_TRAINING.append({
            "id": emp_training_id,
            "employee_id": emp_id,
            "course_id": c["id"],
            "status": status,
            "score": round(random.uniform(65, 100), 1) if status in ["Completed", "Expired"] else "",
            "completion_date": comp_date.isoformat() if comp_date else "",
            "expiry_date": exp_date.isoformat() if exp_date else "",
            "hours_completed": round(hours, 1),
            "certificate_issued": "True" if status == "Completed" else "False",
            "notes": ""
        })
        emp_training_id += 1

# Limit to ~3000 records
EMP_TRAINING = EMP_TRAINING[:3000]

# Write employee_training.csv
with open("data/raw/employee_training.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "course_id", "status", "score", "completion_date", "expiry_date", "hours_completed", "certificate_issued", "notes"])
    writer.writeheader()
    writer.writerows(EMP_TRAINING)

# 8. Role Skill Requirements
ROLE_SKILLS = []
role_skill_id = 1
for role in ROLES:
    role_id = role["id"]
    dept_id = role["department_id"]
    
    # Match skills based on department
    dept = [d for d in DEPARTMENTS if d["id"] == dept_id][0]
    dept_skills = [s for s in SKILLS if s["category"] == ("Technical" if dept_id in [1,2,3,4,5,6] else ("Digital" if dept_id in [8,9] else "Behavioral"))]
    
    # Always include safety skills
    safety_skills = [s for s in SKILLS if s["category"] == "Safety"]
    skills_pool = dept_skills + safety_skills
    
    # Select 4-6 requirements
    chosen_skills = random.sample(skills_pool, min(len(skills_pool), random.randint(4, 6)))
    
    for sk in chosen_skills:
        ROLE_SKILLS.append({
            "id": role_skill_id,
            "role_id": role_id,
            "skill_id": sk["id"],
            "required_level": random.choice(["Intermediate", "Advanced", "Expert"]),
            "is_mandatory": "True" if sk["category"] == "Safety" or random.random() > 0.5 else "False",
            "notes": ""
        })
        role_skill_id += 1

# Write role_skill_requirements.csv
with open("data/raw/role_skill_requirements.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "role_id", "skill_id", "required_level", "is_mandatory", "notes"])
    writer.writeheader()
    writer.writerows(ROLE_SKILLS)

# 9. Career Goals (~500 goals)
CAREER_GOALS = []
goal_id = 1
for emp in EMPLOYEES:
    emp_id = emp["id"]
    grade = emp["grade"]
    
    # Find a role with higher grade
    target_roles = [r for r in ROLES if r["grade"] > grade]
    target_role = random.choice(target_roles) if target_roles else random.choice(ROLES)
    
    CAREER_GOALS.append({
        "id": goal_id,
        "employee_id": emp_id,
        "target_role_id": target_role["id"],
        "target_role_name": target_role["title"],
        "target_timeline_months": random.choice([12, 18, 24]),
        "current_progress_pct": round(random.uniform(0.0, 70.0), 1),
        "status": "Active",
        "notes": "Aligned with annual career development plan."
    })
    goal_id += 1

# Write career_goals.csv
with open("data/raw/career_goals.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "target_role_id", "target_role_name", "target_timeline_months", "current_progress_pct", "status", "notes"])
    writer.writeheader()
    writer.writerows(CAREER_GOALS)

# 10. Performance Reviews (~1000 reviews over 5 cycles)
PERFORMANCE = []
perf_id = 1
cycles = ["FY2021-22", "FY2022-23", "FY2023-24", "FY2024-25", "FY2025-26"]
ratings = ["Meets Expectations", "Exceeds Expectations", "Exceptional", "Partially Meets Expectations"]
score_map = {
    "Exceptional": 5.0,
    "Exceeds Expectations": 4.0,
    "Meets Expectations": 3.0,
    "Partially Meets Expectations": 2.0
}

for emp in EMPLOYEES:
    emp_id = emp["id"]
    # Seed 2-3 historical reviews per employee
    num_reviews = random.randint(2, 3)
    chosen_cycles = random.sample(cycles, num_reviews)
    
    for cycle in chosen_cycles:
        rating = random.choice(ratings)
        review_date = datetime.utcnow() - timedelta(days=random.randint(30, 365 * 2))
        
        PERFORMANCE.append({
            "id": perf_id,
            "employee_id": emp_id,
            "review_cycle": cycle,
            "rating": rating,
            "score": score_map[rating],
            "strengths": "Demonstrates consistent execution and team work.",
            "improvement_areas": "Needs to acquire digital skills and safety certifications.",
            "manager_comments": "Hardworking and reliable team member.",
            "reviewer_name": generate_random_name(),
            "review_date": review_date.isoformat(),
            "is_final": "True"
        })
        perf_id += 1

# Limit to ~1000 reviews
PERFORMANCE = PERFORMANCE[:1000]

# Write performance_reviews.csv
with open("data/raw/performance_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "review_cycle", "rating", "score", "strengths", "improvement_areas", "manager_comments", "reviewer_name", "review_date", "is_final"])
    writer.writeheader()
    writer.writerows(PERFORMANCE)

# 11. ML Forecasts, Predictions, Readiness, risks
# Just generate metadata & simple seed data so that Phase 5 queries work
FORECASTS = []
fc_id = 1
for dept in DEPARTMENTS:
    FORECASTS.append({
        "id": fc_id,
        "department_id": dept["id"],
        "target_year": 2027,
        "current_headcount": random.randint(30, 60),
        "projected_headcount": random.randint(32, 62),
        "required_headcount": random.randint(35, 70),
        "gap": random.randint(3, 10)
    })
    fc_id += 1

with open("data/raw/workforce_forecasts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "department_id", "target_year", "current_headcount", "projected_headcount", "required_headcount", "gap"])
    writer.writeheader()
    writer.writerows(FORECASTS)

SKILL_PREDICTIONS = []
sp_id = 1
for sk in SKILLS[:20]:
    SKILL_PREDICTIONS.append({
        "id": sp_id,
        "skill_id": sk["id"],
        "target_year": 2027,
        "demand_category": random.choice(["High", "Critical"]),
        "confidence_score": round(random.uniform(0.75, 0.95), 2)
    })
    sp_id += 1

with open("data/raw/skill_predictions.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "skill_id", "target_year", "demand_category", "confidence_score"])
    writer.writeheader()
    writer.writerows(SKILL_PREDICTIONS)

READINESS = []
rd_id = 1
# Generate readiness for Gareth targeting role 6 (EAF Mechanical Specialist)
READINESS.append({
    "id": rd_id,
    "employee_id": 1,
    "target_role_id": 6,
    "readiness_score": 60.5,
    "classification": "Developing"
})
rd_id += 1

# Generate other readiness
for emp in EMPLOYEES[1:50]:
    READINESS.append({
        "id": rd_id,
        "employee_id": emp["id"],
        "target_role_id": random.choice([r["id"] for r in ROLES if r["grade"] > emp["grade"]] or [r["id"] for r in ROLES]),
        "readiness_score": round(random.uniform(30.0, 95.0), 1),
        "classification": random.choice(["Not Ready", "Developing", "Nearly Ready", "Ready"])
    })
    rd_id += 1

with open("data/raw/employee_readiness.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "employee_id", "target_role_id", "readiness_score", "classification"])
    writer.writeheader()
    writer.writerows(READINESS)

RISKS = []
rk_id = 1
for dept in DEPARTMENTS:
    # 1 critical risk per dept
    sk = random.choice([s for s in SKILLS if s["category"] in ["Technical", "Safety"]])
    RISKS.append({
        "id": rk_id,
        "department_id": dept["id"],
        "skill_id": sk["id"],
        "risk_type": random.choice(["Single-person Dependency", "Skill Deficiency", "Retirement Risk"]),
        "risk_level": random.choice(["High", "Critical"]),
        "description": f"Critical dependency on single personnel for skill {sk['name']}."
    })
    rk_id += 1

with open("data/raw/skill_risks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "department_id", "skill_id", "risk_type", "risk_level", "description"])
    writer.writeheader()
    writer.writerows(RISKS)

print("Raw CSV files successfully generated in data/raw!")
