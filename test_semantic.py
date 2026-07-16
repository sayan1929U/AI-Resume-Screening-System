from app.services.semantic_matcher import semantic_similarity

resume = """
Python
FastAPI
Docker
AWS
PostgreSQL
REST APIs
"""

jd = """
Python FastAPI Docker AWS PostgreSQL
"""

print(semantic_similarity(resume, jd))