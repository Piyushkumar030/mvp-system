# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend import models, schemas
from datetime import date

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leave Management API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check
@app.get("/")
def health():
    return {"status": "ok"}

# Add employee
@app.post("/employees", response_model=schemas.EmployeeResponse)
def add_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_emp = db.query(models.Employee).filter(models.Employee.email == emp.email).first()
    if db_emp:
        raise HTTPException(status_code=400, detail="Email already exists")
    new_emp = models.Employee(
        name=emp.name,
        email=emp.email,
        department=emp.department,
        joining_date=emp.joining_date
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

# List all employees
@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def list_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

# Apply leave
@app.post("/leave/apply", response_model=schemas.LeaveResponse)
def apply_leave(req: schemas.LeaveRequestCreate, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == req.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if req.start_date < emp.joining_date:
        raise HTTPException(status_code=400, detail="Cannot apply leave before joining date")
    
    overlapping = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.employee_id == emp.id,
        models.LeaveRequest.end_date >= req.start_date,
        models.LeaveRequest.start_date <= req.end_date
    ).first()
    if overlapping:
        raise HTTPException(status_code=400, detail="Overlapping leave exists")
    
    leave = models.LeaveRequest(
        employee_id=emp.id,
        start_date=req.start_date,
        end_date=req.end_date,
        status="pending"
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave

# List leaves for an employee
@app.get("/leave/{employee_id}", response_model=list[schemas.LeaveResponse])
def list_leaves(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db.query(models.LeaveRequest).filter(models.LeaveRequest.employee_id == employee_id).all()
