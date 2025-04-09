import requests
from bs4 import BeautifulSoup

def get_usd_rate():
    try:
        url = "https://minfin.com.ua/currency/usd/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        rate = soup.select_one(".sc-1x32wa2-9.kLFQzH span").text
        rate = rate.replace(",", ".")
        return float(rate)
    except Exception as e:
        print("Currency parsing error:", e)
        return None
