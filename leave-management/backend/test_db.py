# backend/test_db.py
from backend.database import engine, Base
from backend.models import Employee, LeaveRequest

# create tables
Base.metadata.create_all(bind=engine)
print("Tables created successfully")
