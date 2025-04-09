from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/expenses/", response_model=schemas.Expense)
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db, expense)

@app.get("/expenses/", response_model=list[schemas.Expense])
def read_expenses(start_date: str = None, end_date: str = None, db: Session = Depends(get_db)):
    return crud.get_expenses(db, start_date, end_date)

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    success = crud.delete_expense(db, expense_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"detail": "Expense deleted"}

@app.put("/expenses/{expense_id}", response_model=schemas.Expense)
def update_expense(expense_id: int, update_data: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    expense = crud.update_expense(db, expense_id, update_data)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense
