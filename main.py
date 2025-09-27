from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime
import os
from app.schemas.schemas import ShiftCloseRequest
from app.services.telegram import send_telegram_report
from app.services.shifts import (
    calculate_cash_total,
    get_shift_type,
    build_shift_data,
    format_shift_report,
)
from app.models.models import create_db_and_tables, SessionDep, Sale, Expense

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Указываем папку с шаблонами
templates = Jinja2Templates(directory="templates")

# Папка для хранения смен
os.makedirs("shifts", exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Главная страница"}
    )


@app.get("/history")
def get_history(session: SessionDep):
    """
    Получение всей истории для фронта.
    Возвращаем список продаж и расходов отдельно для фронта.
    """
    sales = session.query(Sale).all()
    expenses = session.query(Expense).all()

    sales_list = [
        {
            "date": s.date,
            "shift": s.shift,
            "shift_person": s.shift_person,
            "sale": s.sale,
            "price": s.price,
            "pay_method": s.pay_method,
        }
        for s in sales
    ]

    expenses_list = [
        {
            "date": e.date,
            "shift": e.shift,
            "shift_person": e.shift_person,
            "amount": e.amount,
            "description": e.description,
        }
        for e in expenses
    ]

    return {"sales": sales_list, "expenses": expenses_list}


@app.post("/close_shift")
async def close_shift(session: SessionDep, data: ShiftCloseRequest = Body(...)):
    os.makedirs("shifts", exist_ok=True)
    now = datetime.now()
    shift_type = get_shift_type(now)
    cash_total = calculate_cash_total(data.start_cash, data.sales, data.expenses)
    shift_data = build_shift_data(data, cash_total, shift_type, now)

    filename = f"shifts/shift_{now.strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(shift_data, f, ensure_ascii=False, indent=4)

    for s in data.sales:
        sale = Sale(
            date=s.date,
            shift=s.shift,
            shift_person=s.shift_person,
            sale=s.sale,
            price=s.price,
            pay_method=s.pay_method,
        )
        session.add(sale)

    # Сохраняем расходы в БД
    for e in data.expenses:
        expense = Expense(
            date=e.date,
            shift=e.shift,
            shift_person=e.shift_person,
            amount=e.amount,
            description=e.description,
        )
        session.add(expense)

    session.commit()

    report = format_shift_report(shift_data)
    send_telegram_report(report)

    return JSONResponse(
        {"status": "success", "file": filename, "telegram_report": report}
    )
