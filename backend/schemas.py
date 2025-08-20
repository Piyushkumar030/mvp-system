# backend/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import date

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    joining_date: date

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    joining_date: date
    leave_balance: int

    class Config:
        from_attributes = True

class LeaveRequestCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date

class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    status: str

    class Config:
        from_attributes = True
