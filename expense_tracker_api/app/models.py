from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount_uah = Column(Float, nullable=False)
    amount_usd = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
