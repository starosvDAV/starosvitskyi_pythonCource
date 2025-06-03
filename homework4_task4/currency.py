import requests
import logging

API_KEY = "your_api_key_here"

def convert_currency(from_curr, to_curr, amount):
    if from_curr == to_curr:
        return amount
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}&currencies={to_curr}&base_currency={from_curr}"
    try:
        res = requests.get(url)
        rate = res.json()["data"][to_curr]
        return round(amount * rate, 2)
    except Exception as e:
        logging.warning(f"Currency conversion failed: {e}")
        return amount  # fallback
