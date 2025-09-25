from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime
import os
from app.schemas.schemas import ShiftCloseRequest
from app.services.send_telegram_report import send_telegram_report

app = FastAPI()

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

    # Определяем, день или ночь
    now = datetime.now()
    shift_type = "день" if 8 <= now.hour < 20 else "ночь"

    # Вычисляем общую сумму налички
    cash_total = data.start_cash
    for sale in data.sales:
        if sale.pay_method == "Наличные":
            cash_total += sale.price
    for exp in data.expenses:
        cash_total -= exp.amount

    # Формируем объект для сохранения
    shift_data = {
        "date": now.strftime("%Y-%m-%d"),
        "shift": shift_type,
        "shift_person": data.sales[0].shift_person
        if data.sales
        else (data.expenses[0].shift_person if data.expenses else "—"),
        "cash_total": cash_total,
        "sales": [sale.dict() for sale in data.sales],
        "expenses": [exp.dict() for exp in data.expenses],
        "closed_at": now.isoformat(),
    }

    # Генерируем имя файла
    filename = f"shifts/shift_{now.strftime('%Y%m%d_%H%M%S')}.json"

    # Сохраняем файл
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(shift_data, f, ensure_ascii=False, indent=4)

    # Формируем текст отчёта для Telegram
    sales_text = (
        "\n".join([f"- {s.sale}: {s.price} сом ({s.pay_method})" for s in data.sales])
        or "Нет продаж"
    )
    expenses_text = (
        "\n".join([f"- {e.description}: {e.amount} сом" for e in data.expenses])
        or "Нет трат"
    )

    report = (
        f"Дата: {shift_data['date']}\n"
        # f"Смена: {shift_data['shift']}\n"
        f"Сменщик: {shift_data['shift_person']}\n\n"
        f"Продажи:\n{sales_text}\n\n"
        f"Траты:\n{expenses_text}\n\n"
        f"В кассе: {cash_total} сом"
    )

    send_telegram_report(report)

    return JSONResponse(
        {
            "status": "success",
            "sales_saved": len(data.sales),
            "expenses_saved": len(data.expenses),
            "cash_total": cash_total,
            "file": filename,
            "telegram_report": report,
        }
    )
