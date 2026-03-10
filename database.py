from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date

SQLALCHEMY_DATABASE_URL = "sqlite:////home/hdixon/dateminder/employees.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    birthday = Column(String)  # Stored as ISO string for simplicity
    join_date = Column(String)

# Create the tables
Base.metadata.create_all(bind=engine)
