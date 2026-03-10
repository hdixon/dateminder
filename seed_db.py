from database import SessionLocal, Employee, Base, engine

# Initialize database
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Check if we already have employees
    if db.query(Employee).count() > 0:
        print("Database already seeded.")
        db.close()
        return

    # Original array data
    employees_data = [
        {"name": "Alice Johnson", "birthday": "1990-03-17", "join_date": "2020-03-17"},
        {"name": "Bob Smith", "birthday": "1985-05-10", "join_date": "2018-06-01"},
        {"name": "Charlie Davis", "birthday": "1992-03-12", "join_date": "2022-01-15"},
        {"name": "Diana Prince", "birthday": "1988-12-25", "join_date": "2015-11-10"},
        {"name": "Evan Wright", "birthday": "1995-03-15", "join_date": "2023-03-15"},
    ]

    for emp in employees_data:
        db_emp = Employee(
            name=emp["name"],
            birthday=emp["birthday"],
            join_date=emp["join_date"]
        )
        db.add(db_emp)
    
    db.commit()
    print("Successfully seeded database with original employee data.")
    db.close()

if __name__ == "__main__":
    seed_data()
