"""Populate CampusLaunch with realistic demo data using the Django ORM.

    python manage.py seed_data            # idempotent: safe to run repeatedly
    python manage.py seed_data --reset    # wipe demo data first

Logins (all demo accounts): password Campus@123   |   admin / Admin@123
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from applications.models import Application
from applications.services import change_status
from notifications.models import Notification
from notifications.services import notify
from opportunities.models import Opportunity, OpportunitySkill, Organization, SavedOpportunity
from skills.models import Skill, StudentSkill
from students.models import Certification, Education, Project, StudentProfile

PASSWORD = "Campus@123"

SKILLS = {
    "Programming": ["Python", "Java", "C++", "JavaScript", "TypeScript", "SQL", "Go"],
    "Backend": ["Django", "Flask", "Node.js", "REST API", "MySQL", "PostgreSQL", "MongoDB", "Redis"],
    "Frontend": ["HTML", "CSS", "React", "Bootstrap", "Tailwind CSS"],
    "DevOps": ["Git", "Docker", "AWS", "Linux", "CI/CD", "Kubernetes"],
    "Data & AI": ["Pandas", "NumPy", "Machine Learning", "Data Visualization", "TensorFlow", "Power BI"],
    "Design": ["Figma", "UI/UX Design"],
    "Soft Skills": ["Communication", "Public Speaking", "Leadership", "Technical Writing"],
    "Security": ["Cybersecurity", "Networking"],
}

RECRUITERS = [
    ("recruiter_technova", "hr@technova.example", "TechNova Solutions", "Ahmedabad", "https://technova.example"),
    ("recruiter_cloudspark", "talent@cloudspark.example", "CloudSpark Labs", "Bengaluru", "https://cloudspark.example"),
    ("recruiter_edubridge", "team@edubridge.example", "EduBridge Foundation", "Pune", "https://edubridge.example"),
]

# username, full name, location, goal, skills {name: (level, years)}
STUDENTS = [
    ("aarav", "Aarav Patel", "Ahmedabad", "Django backend developer",
     {"Python": ("Advanced", 2.5), "Django": ("Advanced", 2), "MySQL": ("Intermediate", 1.5), "JavaScript": ("Intermediate", 1.5),
      "Git": ("Intermediate", 2), "HTML": ("Advanced", 2), "CSS": ("Intermediate", 2), "REST API": ("Intermediate", 1)}),
    ("diya", "Diya Shah", "Ahmedabad", "Full stack web developer",
     {"JavaScript": ("Advanced", 2), "React": ("Intermediate", 1), "HTML": ("Expert", 3), "CSS": ("Advanced", 3),
      "Node.js": ("Intermediate", 1), "Git": ("Intermediate", 1.5), "Bootstrap": ("Advanced", 2)}),
    ("rohan", "Rohan Mehta", "Mumbai", "Data scientist",
     {"Python": ("Advanced", 3), "Pandas": ("Advanced", 2), "NumPy": ("Advanced", 2), "Machine Learning": ("Intermediate", 1),
      "SQL": ("Intermediate", 2), "Data Visualization": ("Intermediate", 1.5)}),
    ("isha", "Isha Verma", "Pune", "Cloud and DevOps engineer",
     {"Linux": ("Advanced", 2), "Docker": ("Intermediate", 1), "AWS": ("Intermediate", 1), "Git": ("Advanced", 2),
      "Python": ("Intermediate", 1.5), "CI/CD": ("Beginner", 0.5)}),
    ("kabir", "Kabir Singh", "Delhi", "Software engineer",
     {"Java": ("Advanced", 3), "C++": ("Intermediate", 2), "SQL": ("Intermediate", 2), "Git": ("Intermediate", 2),
      "MySQL": ("Intermediate", 1.5)}),
    ("meera", "Meera Nair", "Bengaluru", "UI/UX designer",
     {"Figma": ("Expert", 3), "UI/UX Design": ("Advanced", 3), "HTML": ("Intermediate", 1.5), "CSS": ("Intermediate", 1.5),
      "Communication": ("Advanced", 3)}),
    ("neel", "Neel Joshi", "Ahmedabad", "Python backend developer",
     {"Python": ("Intermediate", 1.5), "Flask": ("Intermediate", 1), "PostgreSQL": ("Beginner", 0.5), "Git": ("Beginner", 1),
      "REST API": ("Beginner", 0.5)}),
    ("sara", "Sara Khan", "Hyderabad", "Cybersecurity analyst",
     {"Cybersecurity": ("Intermediate", 1.5), "Networking": ("Advanced", 2), "Linux": ("Intermediate", 2), "Python": ("Beginner", 1)}),
]

D = timedelta
# title, org index, type, location, remote, pay, deadline offset days, skills {name: weight}, description
OPPS = [
    ("Django Intern", 0, "internship", "Ahmedabad", False, "INR 15,000 / month", 20,
     {"Python": 3, "Django": 3, "MySQL": 2, "JavaScript": 2, "Git": 1, "Docker": 1},
     "Build and ship features on our Django platform alongside senior engineers."),
    ("Python Backend Developer", 0, "job", "Ahmedabad", False, "INR 6 - 9 LPA", 30,
     {"Python": 3, "Django": 3, "REST API": 3, "MySQL": 2, "Git": 2, "Redis": 2},
     "Design REST APIs and background jobs for a growing SaaS product."),
    ("Full Stack Developer", 1, "job", "Bengaluru", True, "INR 8 - 12 LPA", 25,
     {"Python": 3, "Django": 2, "JavaScript": 3, "HTML": 2, "CSS": 1, "Git": 2, "React": 3},
     "Own features end to end across a Django API and React front end."),
    ("Cloud Backend Associate", 1, "job", "Remote", True, "INR 7 - 10 LPA", 18,
     {"Python": 1, "Django": 1, "MySQL": 1, "JavaScript": 1, "Docker": 1, "AWS": 1},
     "Deploy and operate containerised services on AWS."),
    ("Frontend Developer Intern", 0, "internship", "Ahmedabad", True, "INR 12,000 / month", 14,
     {"HTML": 3, "CSS": 3, "JavaScript": 3, "React": 2, "Git": 1},
     "Turn designs into fast, accessible interfaces."),
    ("Data Science Intern", 1, "internship", "Bengaluru", True, "INR 20,000 / month", 22,
     {"Python": 3, "Pandas": 3, "NumPy": 2, "Machine Learning": 3, "SQL": 2},
     "Clean, analyse and model product usage data."),
    ("CampusHack 2026", 0, "hackathon", "Ahmedabad", False, "Prizes worth INR 1,00,000", 12,
     {"Python": 2, "JavaScript": 2, "Git": 1, "Communication": 1},
     "A 36-hour hackathon for student teams building tools for campus life."),
    ("Women in Tech Scholarship", 2, "scholarship", "Remote", True, "INR 50,000 grant", 40,
     {"Communication": 2, "Python": 1, "Leadership": 2},
     "Scholarship for women pursuing a degree in computing."),
    ("Django Workshop Weekend", 2, "workshop", "Pune", False, "Free", 9,
     {"Python": 2, "Django": 3, "Git": 1},
     "Hands-on weekend workshop: build and deploy a Django app."),
    ("AWS Cloud Practitioner Prep", 1, "certification", "Remote", True, "Voucher included", 35,
     {"AWS": 3, "Linux": 2, "Networking": 1},
     "Guided prep programme with an exam voucher."),
    ("Campus Tech Meetup", 2, "event", "Pune", False, "Free", 6,
     {"Communication": 2, "Public Speaking": 1},
     "Meet engineers, share projects and find teammates."),
    ("Freelance Web Developer", 0, "freelance", "Remote", True, "INR 25,000 / project", 16,
     {"HTML": 3, "CSS": 3, "JavaScript": 2, "Bootstrap": 2},
     "Build marketing sites for small businesses."),
    ("UI/UX Design Intern", 2, "internship", "Pune", True, "INR 10,000 / month", 21,
     {"Figma": 3, "UI/UX Design": 3, "Communication": 1},
     "Design flows and prototypes for our learning products."),
    ("Security Analyst Trainee", 1, "job", "Hyderabad", False, "INR 5 - 7 LPA", 28,
     {"Cybersecurity": 3, "Networking": 3, "Linux": 2, "Python": 1},
     "Monitor, triage and harden production systems."),
    ("Java Software Engineer", 1, "job", "Delhi", False, "INR 9 - 14 LPA", 33,
     {"Java": 3, "SQL": 2, "MySQL": 2, "Git": 1, "REST API": 2},
     "Build services for a high-traffic payments platform."),
    ("Legacy Data Migration Intern", 0, "internship", "Ahmedabad", False, "INR 8,000 / month", -5,
     {"SQL": 3, "Python": 2},
     "Expired demo posting: appears in admin stats but not in search."),
]

# student username -> [(opportunity title, final status)]
APPLICATIONS = {
    "aarav": [("Django Intern", "Shortlisted"), ("Python Backend Developer", "Applied")],
    "neel": [("Django Intern", "Under Review"), ("Python Backend Developer", "Applied")],
    "diya": [("Full Stack Developer", "Interview"), ("Frontend Developer Intern", "Selected"), ("Django Intern", "Rejected")],
    "rohan": [("Data Science Intern", "Shortlisted")],
    "isha": [("Cloud Backend Associate", "Under Review"), ("AWS Cloud Practitioner Prep", "Applied")],
    "kabir": [("Java Software Engineer", "Applied")],
    "meera": [("UI/UX Design Intern", "Selected")],
    "sara": [("Security Analyst Trainee", "Interview")],
}


class Command(BaseCommand):
    help = "Create demo users, skills, opportunities, applications and notifications."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing demo data first.")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["reset"]:
            self._reset()
        today = timezone.localdate()

        admin, created = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@campuslaunch.example", "is_staff": True, "is_superuser": True})
        if created:
            admin.set_password("Admin@123")
            admin.save()

        skill_by_name = {}
        for category, names in SKILLS.items():
            for name in names:
                skill_by_name[name], _ = Skill.objects.get_or_create(name=name, defaults={"category": category})

        orgs = []
        for username, email, org_name, city, site in RECRUITERS:
            user, made = User.objects.get_or_create(
                username=username, defaults={"email": email, "role": User.Role.RECRUITER})
            if made:
                user.set_password(PASSWORD)
                user.save()
            org, _ = Organization.objects.get_or_create(
                owner=user, defaults={"name": org_name, "location": city, "website": site,
                                      "description": f"{org_name} hires and trains early-career talent."})
            orgs.append(org)

        profiles = {}
        for username, full_name, city, goal, skills in STUDENTS:
            user, made = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@student.example", "role": User.Role.STUDENT})
            if made:
                user.set_password(PASSWORD)
                user.save()
            profile, _ = StudentProfile.objects.get_or_create(user=user, defaults={
                "full_name": full_name, "location": city, "career_goal": goal, "phone": "+91 98765 43210",
                "bio": f"Final-year student interested in {goal.lower()} roles.",
                "github_url": f"https://github.com/{username}-demo"})
            profiles[username] = profile
            for name, (level, years) in skills.items():
                StudentSkill.objects.get_or_create(
                    student=profile, skill=skill_by_name[name], defaults={"level": level, "years": years})
            Education.objects.get_or_create(
                student=profile, degree="B.Tech", institution="Gujarat Technological University",
                defaults={"field_of_study": "Computer Engineering", "start_date": today.replace(year=today.year - 4, month=7, day=1),
                          "end_date": today.replace(year=today.year, month=6, day=30), "grade": "8.4 CGPA"})
            Project.objects.get_or_create(
                student=profile, title=f"{full_name.split()[0]}'s Capstone Project",
                defaults={"description": "Team project built for the final-year curriculum.",
                          "technologies": ", ".join(list(skills)[:3])})
            if username in ("aarav", "rohan", "isha"):
                Certification.objects.get_or_create(
                    student=profile, name="Professional Certificate", issuer="Coursera",
                    defaults={"issued_on": today - D(days=120)})

        opp_by_title = {}
        for title, org_i, kind, city, remote, pay, offset, req, desc in OPPS:
            opp, made = Opportunity.objects.get_or_create(
                organization=orgs[org_i], title=title,
                defaults={"opportunity_type": kind, "location": city, "is_remote": remote,
                          "compensation": pay, "deadline": today + D(days=offset), "description": desc})
            opp_by_title[title] = opp
            if made:
                OpportunitySkill.objects.bulk_create(
                    [OpportunitySkill(opportunity=opp, skill=skill_by_name[n], weight=w) for n, w in req.items()])

        for username, entries in APPLICATIONS.items():
            for title, final in entries:
                app, made = Application.objects.get_or_create(student=profiles[username], opportunity=opp_by_title[title])
                if made:
                    notify(profiles[username].user, f"You applied to {title}.", f"/opportunities/{opp_by_title[title].pk}/")
                    notify(opp_by_title[title].organization.owner, f"New application from {profiles[username]} for {title}.",
                           f"/recruiter/opportunities/{opp_by_title[title].pk}/applicants/")
                    if final != Application.Status.APPLIED:
                        change_status(app, final)

        for username, title in [("aarav", "Cloud Backend Associate"), ("aarav", "Full Stack Developer"), ("diya", "CampusHack 2026")]:
            SavedOpportunity.objects.get_or_create(student=profiles[username], opportunity=opp_by_title[title])

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {User.objects.count()} users, {Skill.objects.count()} skills, {Opportunity.objects.count()} opportunities, "
            f"{Application.objects.count()} applications, {Notification.objects.count()} notifications."))
        self.stdout.write("Logins -> admin / Admin@123 | aarav (student), recruiter_technova (recruiter) / Campus@123")

    def _reset(self):
        Application.objects.all().delete()
        Opportunity.objects.all().delete()
        Organization.objects.all().delete()
        StudentProfile.objects.all().delete()
        Notification.objects.all().delete()
        StudentSkill.objects.all().delete()
        Skill.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
