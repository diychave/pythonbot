from pydantic import BaseModel
from datetime import date


class ExpenseBase(BaseModel):
    name: str
    amount_uah: float
    amount_usd: float
    date: date

class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int

    class Config:
        orm_mode = True
