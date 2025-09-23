from pydantic import BaseModel
from typing import List


class SaleCreate(BaseModel):
    date: str
    shift: str
    shift_person: str  # обязательно
    sale: str  # обязательно
    price: float  # обязательно
    pay_method: str  # обязательно


class ExpenseCreate(BaseModel):
    date: str
    shift: str
    shift_person: str  # обязательно
    amount: float  # обязательно
    description: str  # обязательно


class ShiftCloseRequest(BaseModel):
    sales: List[SaleCreate]
    expenses: List[ExpenseCreate]
    start_cash: float  # стартовая сумма кассы
    cash_total: float  # итоговая сумма наличкой
