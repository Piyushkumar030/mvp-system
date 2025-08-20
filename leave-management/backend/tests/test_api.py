import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models import Employee, LeaveRequest
from backend.database import Base, engine, get_db

# Fixture to setup and teardown the test database
@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)  # create tables
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)  # drop tables after tests

# Helper to create an employee
def create_employee(client, name="Test User", email="testuser@example.com", department="IT", joining_date="2024-01-01"):
    payload = {
        "name": name,
        "email": email,
        "department": department,
        "joining_date": joining_date
    }
    response = client.post("/employees", json=payload)
    if response.status_code != 200:
        return response  # return Response object if creation fails
    return response.json()

# Health check
def test_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test adding an employee
def test_add_employee(client):
    emp = create_employee(client)
    if isinstance(emp, dict):
        assert emp["name"] == "Test User"
        assert emp["department"] == "IT"
        assert emp["leave_balance"] == 12
    else:
        pytest.fail(f"Add employee failed: {emp.status_code} {emp.json()}")

# Test leave application before joining date
def test_leave_before_joining(client):
    emp = create_employee(client, email="early@example.com", joining_date="2025-01-01")
    if isinstance(emp, dict):
        payload = {
            "employee_id": emp["id"],
            "start_date": "2024-12-20",
            "end_date": "2024-12-25"
        }
        response = client.post("/leave/apply", json=payload)
        assert response.status_code == 400
    else:
        pytest.fail(f"Employee creation failed: {emp.status_code} {emp.json()}")

# Test successful leave application
def test_leave_apply_success(client):
    emp = create_employee(client, email="success@example.com")
    if isinstance(emp, dict):
        payload = {
            "employee_id": emp["id"],
            "start_date": "2025-08-20",
            "end_date": "2025-08-22"
        }
        response = client.post("/leave/apply", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == emp["id"]
        assert data["status"] == "pending"  # match API lowercase status
    else:
        pytest.fail(f"Employee creation failed: {emp.status_code} {emp.json()}")

# Test leave application for non-existent employee
def test_leave_for_nonexistent_employee(client):
    payload = {
        "employee_id": 9999,
        "start_date": "2025-08-20",
        "end_date": "2025-08-22"
    }
    response = client.post("/leave/apply", json=payload)
    assert response.status_code == 404
