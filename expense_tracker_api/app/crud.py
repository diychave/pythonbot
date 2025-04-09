from sqlalchemy.orm import Session
from . import models, schemas
from .currency_parser import get_usd_rate

def get_expenses(db: Session, start_date=None, end_date=None):
    query = db.query(models.Expense)
    if start_date and end_date:
        query = query.filter(models.Expense.date.between(start_date, end_date))
    return query.all()

def create_expense(db: Session, expense: schemas.ExpenseCreate):
    usd_rate = get_usd_rate()
    amount_usd = expense.amount_uah / usd_rate if usd_rate else 0.0
    db_expense = models.Expense(
        title=expense.title,
        date=expense.date,
        amount_uah=expense.amount_uah,
        amount_usd=amount_usd
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
        return True
    return False

def update_expense(db: Session, expense_id: int, update_data: schemas.ExpenseUpdate):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if expense:
        usd_rate = get_usd_rate()
        expense.title = update_data.title
        expense.amount_uah = update_data.amount_uah
        expense.amount_usd = update_data.amount_uah / usd_rate if usd_rate else 0.0
        db.commit()
        db.refresh(expense)
        return expense
    return None
