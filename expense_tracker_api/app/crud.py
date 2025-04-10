from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date


def create_expense(db: Session, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(
        name=expense.name,
        amount_uah=expense.amount_uah,
        amount_usd=expense.amount_usd,
        date=expense.date,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expense(db: Session, expense_id: int):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()


def get_expenses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Expense).offset(skip).limit(limit).all()


def delete_expense(db: Session, expense_id: int):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
    return expense


def update_expense(db: Session, expense_id: int, expense: schemas.ExpenseCreate):
    db_expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if db_expense:
        db_expense.name = expense.name
        db_expense.amount_uah = expense.amount_uah
        db_expense.amount_usd = expense.amount_usd
        db_expense.date = expense.date
        db.commit()
        db.refresh(db_expense)
    return db_expense


def get_expenses_by_date_range(db: Session, start_date: date, end_date: date):
    return db.query(models.Expense).filter(
        models.Expense.date >= start_date,
        models.Expense.date <= end_date
    ).all()
