from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List, Dict, Optional
import os

from database import SessionLocal, Employee

app = FastAPI()

# Create static and templates directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_next_occurrence(event_date_str: str) -> date:
    event_date = date.fromisoformat(event_date_str)
    today = date.today()
    
    # Set the year to current year
    next_date = date(today.year, event_date.month, event_date.day)
    
    # If the date has already passed this year, set it to next year
    if next_date < today:
        next_date = date(today.year + 1, event_date.month, event_date.day)
        
    return next_date

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    db_employees = db.query(Employee).all()
    
    processed_employees = []
    upcoming_notifications = []
    
    for emp in db_employees:
        bday_next = get_next_occurrence(emp.birthday)
        join_next = get_next_occurrence(emp.join_date)
        
        bday_days = (bday_next - today).days
        join_days = (join_next - today).days
        
        orig_join = date.fromisoformat(emp.join_date)
        years = join_next.year - orig_join.year
        
        emp_data = {
            "id": emp.id,
            "name": emp.name,
            "birthday": emp.birthday,
            "join_date": emp.join_date,
            "bday_next": bday_next,
            "bday_days": bday_days,
            "join_next": join_next,
            "join_days": join_days,
            "anniversary_years": years
        }
        
        processed_employees.append(emp_data)
        
        # Check for 7-day notification
        if bday_days == 7:
            upcoming_notifications.append({
                "name": emp.name,
                "event": "Birthday",
                "date": bday_next,
                "message": f"Send birthday card to {emp.name}!"
            })
        
        if join_days == 7:
            upcoming_notifications.append({
                "name": emp.name,
                "event": f"{years} Year Anniversary",
                "date": join_next,
                "message": f"Send anniversary card to {emp.name} for their {years} year mark!"
            })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "employees": processed_employees,
        "notifications": upcoming_notifications,
        "today": today
    })

@app.get("/edit/{employee_id}", response_class=HTMLResponse)
async def edit_employee_form(request: Request, employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "employee": employee})

@app.post("/edit/{employee_id}")
async def edit_employee(
    employee_id: int, 
    name: str = Form(...), 
    birthday: str = Form(...), 
    join_date: str = Form(...),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    employee.name = name
    employee.birthday = birthday
    employee.join_date = join_date
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/add", response_class=HTMLResponse)
async def add_employee_form(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})

@app.post("/add")
async def add_employee(
    name: str = Form(...), 
    birthday: str = Form(...), 
    join_date: str = Form(...),
    db: Session = Depends(get_db)
):
    new_emp = Employee(name=name, birthday=birthday, join_date=join_date)
    db.add(new_emp)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{employee_id}")
async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if employee:
        db.delete(employee)
        db.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
