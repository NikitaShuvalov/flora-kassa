from sqlalchemy import Column, Integer, String, Float
from database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    shift = Column(String, nullable=False)
    shift_person = Column(String, nullable=False)  # обязательно
    sale = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    pay_method = Column(String, nullable=False)  # обязательно


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    shift = Column(String, nullable=False)
    shift_person = Column(String, nullable=False)  # обязательно
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
