from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import json
from datetime import datetime
import os

app = FastAPI()

# Указываем папку с шаблонами
templates = Jinja2Templates(directory="templates")

# Папка для хранения смен
os.makedirs("shifts", exist_ok=True)


# Pydantic схемы
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


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Главная страница"}
    )


@app.get("/history")
def get_history():
    history_list = []
    for filename in os.listdir("shifts"):
        if filename.endswith(".json"):
            with open(os.path.join("shifts", filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                history_list.extend(data.get("sales", []))
                history_list.extend(data.get("expenses", []))
    # Сортировка по дате
    history_list.sort(key=lambda x: x.get("date", ""))
    return history_list


@app.post("/close_shift")
async def close_shift(data: ShiftCloseRequest = Body(...)):
    os.makedirs("shifts", exist_ok=True)

    # Вычисляем общую сумму налички
    cash_total = data.start_cash
    for sale in data.sales:
        if sale.pay_method == "Наличные":
            cash_total += sale.price
    for exp in data.expenses:
        cash_total -= exp.amount

    # Формируем объект для сохранения
    shift_data = {
        "cash_total": cash_total,
        "sales": [sale.dict() for sale in data.sales],
        "expenses": [exp.dict() for exp in data.expenses],
        "closed_at": datetime.now().isoformat(),
    }

    # Генерируем имя файла
    filename = f"shifts/shift_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Сохраняем файл
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(shift_data, f, ensure_ascii=False, indent=4)

    return JSONResponse(
        {
            "status": "success",
            "sales_saved": len(data.sales),
            "expenses_saved": len(data.expenses),
            "cash_total": cash_total,
            "file": filename,
        }
    )
