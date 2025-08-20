# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Employee, LeaveRequest
from backend.database import Base, engine, get_db

from sqlalchemy.orm import sessionmaker

# Create a separate test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    # Create tables before tests
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Drop tables after tests (optional)
    Base.metadata.drop_all(bind=engine)
