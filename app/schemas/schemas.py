from pydantic import BaseModel
from typing import List


class SaleCreate(BaseModel):
    date: str
    shift: str
    shift_person: str
    sale: str
    price: float
    pay_method: str


class ExpenseCreate(BaseModel):
    date: str
    shift: str
    shift_person: str
    amount: float
    description: str


class ShiftCloseRequest(BaseModel):
    sales: List[SaleCreate]
    expenses: List[ExpenseCreate]
    start_cash: float
