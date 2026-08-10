"""Database Seeder Module.

Populates the PostgreSQL database with realistic sample data for an
AI Workforce Intelligence Platform (Manufacturing Organization context).
"""

import random
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from faker import Faker

from app.database.database import SessionLocal, init_db
from app.database.models import (
    Department, JobRole, Skill, Employee, EmployeeSkill,
    TrainingCourse, EmployeeTraining, RoleSkillRequirement,
    PerformanceReview, CareerGoal, SkillLevel, EmploymentStatus,
    TrainingStatus, TrainingMode, PerformanceRating, GoalStatus
)
from app.utils.logger import logger

fake = Faker('en_IN')  # Use Indian locale for names (Tata Steel context)

# ---------------------------------------------------------------------------
# Constants & Master Data
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    {"name": "Mechanical Maintenance", "code": "MECH"},
    {"name": "Electrical & Electronics", "code": "ELEC"},
    {"name": "Automation & Control", "code": "AUTO"},
    {"name": "Blast Furnace Operations", "code": "BF"},
    {"name": "Rolling Mill Operations", "code": "RM"},
    {"name": "Quality Assurance & Metallurgy", "code": "QA"},
    {"name": "Human Resources", "code": "HR"},
    {"name": "Information Technology", "code": "IT"},
    {"name": "AI & Digital Initiatives", "code": "AI"},
    {"name": "Supply Chain & Logistics", "code": "SCM"},
]

SKILL_CATEGORIES = {
    "Technical": ["Hydraulics", "PLC Programming", "Metallurgy", "CNC Machining", "Welding", "SCADA", "Python", "Data Analysis", "Cloud Architecture"],
    "Safety": ["LOTO", "Confined Space", "First Aid", "Fire Safety", "Hazard ID"],
    "Leadership": ["Team Management", "Conflict Resolution", "Strategic Planning", "Coaching"],
    "Digital": ["IoT Sensors", "Digital Twin", "Data Visualization", "Machine Learning", "SAP ERP"],
    "Behavioral": ["Communication", "Problem Solving", "Adaptability", "Time Management"]
}

COURSE_PROVIDERS = ["Tata Steel Digie-Shala", "Coursera", "Internal Training Academy", "Udemy Business", "Original Equipment Manufacturer (OEM)"]

def generate_departments(db: Session) -> List[Department]:
    logger.info("Generating Departments...")
    depts = []
    for d in DEPARTMENTS:
        dept = Department(
            name=d["name"],
            code=d["code"],
            description=f"Handles operations related to {d['name']}",
            head_name=fake.name(),
            location=random.choice(["Jamshedpur Plant", "Kalinganagar Plant", "Meramandali Plant"])
        )
        db.add(dept)
        depts.append(dept)
    db.commit()
    for d in depts:
        db.refresh(d)
    return depts


def generate_job_roles(db: Session, departments: List[Department]) -> List[JobRole]:
    logger.info("Generating Job Roles...")
    roles = []
    titles = ["Technician", "Senior Technician", "Engineer", "Senior Engineer", "Manager", "Senior Manager", "Head"]
    for dept in departments:
        for i, title in enumerate(titles):
            role = JobRole(
                title=f"{title} - {dept.name}",
                department_id=dept.id,
                grade=i + 1,
                track="Leadership" if "Manager" in title or "Head" in title else "Technical",
                min_experience_years=i * 2,
                description=f"Responsible for {title.lower()} tasks in {dept.name}."
            )
            db.add(role)
            roles.append(role)
    db.commit()
    for r in roles:
        db.refresh(r)
    return roles


def generate_skills(db: Session) -> List[Skill]:
    logger.info("Generating Skills...")
    skills = []
    for cat, skill_names in SKILL_CATEGORIES.items():
        for i in range(30):  # Generate around 150 skills (30 per category)
            # Create a mix of generic and specific skills
            name = skill_names[i % len(skill_names)] if i < len(skill_names) else f"{cat} Skill {i}"
            if any(s.name == name for s in skills):
                name = f"{name} {i}"
                
            skill = Skill(
                name=name,
                category=cat,
                subcategory=fake.word().capitalize(),
                description=fake.sentence(),
                future_demand=random.choice(["Low", "Medium", "High"]),
                criticality=random.choice(["Low", "Medium", "High", "Critical"])
            )
            db.add(skill)
            skills.append(skill)
    db.commit()
    for s in skills:
        db.refresh(s)
    return skills


def generate_employees(db: Session, departments: List[Department], roles: List[JobRole]) -> List[Employee]:
    logger.info("Generating Employees...")
    employees = []
    for i in range(100):
        dept = random.choice(departments)
        dept_roles = [r for r in roles if r.department_id == dept.id]
        role = random.choice(dept_roles)
        
        emp = Employee(
            employee_number=f"EMP{1000 + i}",
            name=fake.name(),
            email=f"emp{1000 + i}@tatasteel.mock",
            department_id=dept.id,
            role_id=role.id,
            grade=role.grade,
            years_experience=random.uniform(role.min_experience_years, role.min_experience_years + 15),
            years_in_company=random.uniform(0, 20),
            location=dept.location,
            employment_status=EmploymentStatus.ACTIVE,
            phone=fake.phone_number()
        )
        db.add(emp)
        employees.append(emp)
    db.commit()
    
    # Assign managers (higher grade in same department)
    for emp in employees:
        possible_managers = [m for m in employees if m.department_id == emp.department_id and m.grade > emp.grade]
        if possible_managers:
            emp.manager_id = random.choice(possible_managers).id
            db.add(emp)
    db.commit()
    
    for e in employees:
        db.refresh(e)
    return employees


def generate_courses(db: Session) -> List[TrainingCourse]:
    logger.info("Generating Training Courses...")
    courses = []
    for i in range(80):
        courses.append(TrainingCourse(
            code=f"CRS{100 + i}",
            name=f"{fake.catch_phrase()} Course",
            description=fake.paragraph(),
            category=random.choice(list(SKILL_CATEGORIES.keys())),
            duration_hours=random.choice([2, 4, 8, 16, 40]),
            difficulty=random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
            mode=random.choice(list(TrainingMode)),
            provider=random.choice(COURSE_PROVIDERS),
            is_mandatory=random.random() > 0.8
        ))
    db.add_all(courses)
    db.commit()
    for c in courses:
        db.refresh(c)
    return courses


def generate_employee_skills(db: Session, employees: List[Employee], skills: List[Skill]):
    logger.info("Generating Employee Skills...")
    emp_skills = []
    for _ in range(500):
        emp = random.choice(employees)
        skill = random.choice(skills)
        # Avoid duplicates
        if any(es.employee_id == emp.id and es.skill_id == skill.id for es in emp_skills):
            continue
            
        emp_skills.append(EmployeeSkill(
            employee_id=emp.id,
            skill_id=skill.id,
            level=random.choice(list(SkillLevel)),
            years_experience=random.uniform(0.5, 10.0),
            is_certified=random.random() > 0.5,
            last_assessed=datetime.utcnow() - timedelta(days=random.randint(10, 365))
        ))
    db.add_all(emp_skills)
    db.commit()


def generate_employee_training(db: Session, employees: List[Employee], courses: List[TrainingCourse]):
    logger.info("Generating Employee Training...")
    training_records = []
    for _ in range(200):
        emp = random.choice(employees)
        course = random.choice(courses)
        status = random.choice(list(TrainingStatus))
        
        record = EmployeeTraining(
            employee_id=emp.id,
            course_id=course.id,
            status=status,
            score=random.uniform(60, 100) if status == TrainingStatus.COMPLETED else None,
            completion_date=datetime.utcnow() - timedelta(days=random.randint(1, 300)) if status == TrainingStatus.COMPLETED else None,
            hours_completed=course.duration_hours if status == TrainingStatus.COMPLETED else random.uniform(0, course.duration_hours)
        )
        training_records.append(record)
    db.add_all(training_records)
    db.commit()


def generate_role_skill_reqs(db: Session, roles: List[JobRole], skills: List[Skill]):
    logger.info("Generating Role Skill Requirements...")
    reqs = []
    for role in roles:
        # 3-5 skills per role
        role_skills = random.sample(skills, random.randint(3, 5))
        for skill in role_skills:
            reqs.append(RoleSkillRequirement(
                role_id=role.id,
                skill_id=skill.id,
                required_level=random.choice([SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED, SkillLevel.EXPERT]),
                is_mandatory=random.random() > 0.3
            ))
    db.add_all(reqs)
    db.commit()


def generate_performance_reviews(db: Session, employees: List[Employee]):
    logger.info("Generating Performance Reviews...")
    reviews = []
    # Around 100 reviews
    for emp in random.sample(employees, min(len(employees), 100)):
        rating = random.choice(list(PerformanceRating))
        score_map = {
            PerformanceRating.EXCEPTIONAL: 5.0,
            PerformanceRating.EXCEEDS: 4.0,
            PerformanceRating.MEETS: 3.0,
            PerformanceRating.PARTIAL: 2.0,
            PerformanceRating.DOES_NOT_MEET: 1.0,
        }
        score = score_map[rating]
        reviews.append(PerformanceReview(
            employee_id=emp.id,
            review_cycle="FY2023-24",
            rating=rating,
            score=score,
            strengths=fake.paragraph(),
            improvement_areas=fake.paragraph(),
            manager_comments=fake.paragraph(),
            review_date=datetime.utcnow() - timedelta(days=random.randint(30, 180))
        ))
    db.add_all(reviews)
    db.commit()


def generate_career_goals(db: Session, employees: List[Employee], roles: List[JobRole]):
    logger.info("Generating Career Goals...")
    goals = []
    for emp in random.sample(employees, min(len(employees), 100)):
        # Select a target role that is higher grade than current
        target_roles = [r for r in roles if r.grade > emp.grade]
        target_role = random.choice(target_roles) if target_roles else random.choice(roles)
        
        goals.append(CareerGoal(
            employee_id=emp.id,
            target_role_id=target_role.id,
            target_role_name=target_role.title,
            target_timeline_months=random.choice([12, 24, 36]),
            current_progress_pct=random.uniform(0, 80),
            status=GoalStatus.ACTIVE
        ))
    db.add_all(goals)
    db.commit()


def seed_database():
    """Main seed function."""
    logger.info("Starting Database Seed Process...")
    
    # Ensure tables exist
    init_db()
    
    db: Session = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Department).first():
            logger.info("Database already seeded. Skipping.")
            return

        depts = generate_departments(db)
        roles = generate_job_roles(db, depts)
        skills = generate_skills(db)
        employees = generate_employees(db, depts, roles)
        courses = generate_courses(db)
        
        generate_employee_skills(db, employees, skills)
        generate_employee_training(db, employees, courses)
        generate_role_skill_reqs(db, roles, skills)
        generate_performance_reviews(db, employees)
        generate_career_goals(db, employees, roles)
        
        logger.info("Database seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
