from app.services.nlp_service import extract_skills

resume = """
Python Developer

Skills:
Python
FastAPI
Docker
AWS
PostgreSQL
GitHub
Machine Learning
"""

print(extract_skills(resume))