from app.services.matcher import calculate_similarity

resume = """
Python
FastAPI
SQL
"""

jd = """
Python
FastAPI
Docker
AWS
Redis
"""

print(calculate_similarity(resume, jd))