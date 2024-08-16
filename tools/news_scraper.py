import requests
from bs4 import BeautifulSoup
from newspaper import Article

class NewsScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_news(self, ticker, limit=8):
        url = f"https://sg.finance.yahoo.com/quote/{ticker}/news/"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching the webpage: {e}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('li', class_='stream-item')

        news_data = {}
        count = 0
        for item in news_items:
            if count >= limit:
                break
            element = item.find('a', class_='subtle-link')
            if element:
                title = element['title']
                link = element['href']
                news_data[title] = link
                count += 1

        return news_data

    def collect_news_data(self, news_data):
        articles = {}
        for key, value in news_data.items():
            try:
                article = Article(value)
                article.download()
                article.parse()
                articles[key, value] = article.text
            except Exception as e:
                print(f"Error processing article: {e}")
        return articles

    def scrape_and_collect(self, ticker):
        news_data = self.get_news(ticker)
        if news_data:
            return self.collect_news_data(news_data)
        return None
