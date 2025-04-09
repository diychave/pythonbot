from pydantic import BaseModel
from datetime import date

class ExpenseBase(BaseModel):
    title: str
    date: date
    amount_uah: float

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    title: str
    amount_uah: float

class Expense(ExpenseBase):
    id: int
    amount_usd: float

    class Config:
        orm_mode = True
