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
    now = datetime.now()
    shift_type = get_shift_type(now)
    cash_total = calculate_cash_total(data.start_cash, data.sales, data.expenses)
    shift_data = build_shift_data(data, cash_total, shift_type, now)

    filename = f"shifts/shift_{now.strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(shift_data, f, ensure_ascii=False, indent=4)

    report = format_shift_report(shift_data)

    send_telegram_report(report)

    return JSONResponse(
        {"status": "success", "file": filename, "telegram_report": report}
    )
