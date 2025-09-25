import requests

TELEGRAM_TOKEN = "7753186561:AAEr6OiezYlaOtN4Up2bg0HemY_eoOKMiPM"
CHAT_ID = "752293440"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def send_telegram_report(report: str):
    try:
        response = requests.post(
            TELEGRAM_API_URL,
            data={"chat_id": CHAT_ID, "text": report, "parse_mode": "HTML"},
        )
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")
