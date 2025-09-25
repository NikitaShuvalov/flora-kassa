def calculate_cash_total(start_cash: float, sales: list, expenses: list) -> float:
    total = start_cash
    for s in sales:
        if s.pay_method == "Наличные":
            total += s.price
    for e in expenses:
        total -= e.amount
    return total
