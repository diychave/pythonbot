import aiohttp

EXCHANGE_RATE_API_KEY = '999ebfb504f4f2a287aae75d'
EXCHANGE_RATE_URL = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"

async def get_exchange_rate():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(EXCHANGE_RATE_URL) as response:
                data = await response.json()

                if response.status == 200 and 'conversion_rates' in data:
                    rate = data['conversion_rates'].get('UAH', None)
                    if rate:
                        return rate
                    else:
                        print("UAH курс не найден.")
                        return 1  
                else:
                    print("Не удалось получить данные о курсе валют.")
                    return 1  
    except Exception as e:
        print(f"Ошибка при получении курса валют: {e}")
        return 1 
