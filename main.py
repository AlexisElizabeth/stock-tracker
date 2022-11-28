import os
import re
import requests
from datetime import datetime, timedelta
from twilio.rest import Client


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
ALERT_SENSITIVITY_PERCENTAGE = 1
TWILIO_ACCOUNT_SID = "ACb6a461c9edc5a7209291532ad1ad1c69"

if __name__ == "__main__":
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
    ALPHAVANTAGE_ENDPOINT = "https://www.alphavantage.co/query"
    ALPHAVANTAGE_PARAMETERS = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": api_key
    }

    news_api_key = os.environ.get("NEWSAPI_API_KEY")
    NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"
    NEWSAPI_PARAMETERS = {
        "apikey": news_api_key,
        "q": COMPANY_NAME
    }

    response = requests.get(url=ALPHAVANTAGE_ENDPOINT, params=ALPHAVANTAGE_PARAMETERS)
    response.raise_for_status()
    stock_data = response.json()

    today_date = datetime.now().date()
    yesterday_date = today_date - timedelta(days=1)
    two_days_ago = today_date - timedelta(days=2)

    yesterday_closing = float(stock_data["Time Series (Daily)"][str(yesterday_date)]['4. close'])
    two_days_ago_closing = float(stock_data["Time Series (Daily)"][str(two_days_ago)]['4. close'])

    big_change = False
    percentage_change = round((yesterday_closing - two_days_ago_closing) / two_days_ago_closing * 100, 2)
    if abs(percentage_change) >= ALERT_SENSITIVITY_PERCENTAGE:
        big_change = True

    if big_change:
        response = requests.get(url=NEWSAPI_ENDPOINT, params=NEWSAPI_PARAMETERS)
        response.raise_for_status()
        news_data = response.json()
        news_slice = news_data["articles"][:3]

        title_1 = news_slice[0]["title"]
        desc_1 = news_slice[0]["description"]
        desc_1 = re.sub(r'<.*?>', '', desc_1)

        title_2 = news_slice[1]["title"]
        desc_2 = news_slice[1]["description"]
        desc_2 = re.sub(r'<.*?>', '', desc_2)

        title_3 = news_slice[2]["title"]
        desc_3 = news_slice[2]["description"]
        desc_3 = re.sub(r'<.*?>', '', desc_3)

        if percentage_change > 0:
            icon = "🔺"
        else:
            icon = "🔻"

        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        client = Client(TWILIO_ACCOUNT_SID, auth_token)
        message = client.messages \
            .create(
                body=f"""
    \n
    {STOCK}: {percentage_change}% {icon}\n\n
    Headline: {title_1} \n
    Brief: {desc_1} \n\n
    Headline: {title_2} \n
    Brief: {desc_2} \n\n
    Headline: {title_3} \n
    Brief: {desc_3} \n\n
        """,
                from_="+18022789911",
                to="+46734628624"
            )
