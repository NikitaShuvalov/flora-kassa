from datetime import datetime


def calculate_cash_total(start_cash: float, sales: list, expenses: list) -> float:
    total = start_cash
    for s in sales:
        if s.pay_method == "Наличные":
            total += s.price
    for e in expenses:
        total -= e.amount
    return total


def get_shift_type(current_time: datetime) -> str:
    return "день" if 8 <= current_time.hour < 20 else "ночь"


def build_shift_data(data, cash_total: float, shift_type: str, now: datetime) -> dict:
    shift_person = (
        data.sales[0].shift_person
        if data.sales
        else (data.expenses[0].shift_person if data.expenses else "—")
    )
    return {
        "date": now.strftime("%Y-%m-%d"),
        "shift": shift_type,
        "shift_person": shift_person,
        "start_cash": data.start_cash,
        "cash_total": cash_total,
        "sales": [s.dict() for s in data.sales],
        "expenses": [e.dict() for e in data.expenses],
        "closed_at": now.isoformat(),
    }


def format_shift_report(shift_data: dict) -> str:
    sales_text = (
        "\n".join(
            [
                f"- {s['sale']}: {s['price']} сом ({s['pay_method']})"
                for s in shift_data["sales"]
            ]
        )
        or "Нет продаж"
    )
    expenses_text = (
        "\n".join(
            [f"- {e['description']}: {e['amount']} сом" for e in shift_data["expenses"]]
        )
        or "Нет трат"
    )
    return (
        f"Дата: {shift_data['date']}\n"
        f"Сменщик: {shift_data['shift_person']}\n\n"
        f"Начальная касса: {shift_data['start_cash']} сом\n\n"
        f"Продажи:\n{sales_text}\n\n"
        f"Траты:\n{expenses_text}\n\n"
        f"В кассе: {shift_data['cash_total']} сом"
    )
