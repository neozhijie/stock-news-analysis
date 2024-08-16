from abc import ABC, abstractmethod
from .news_analyzer import NewsAnalyzer
from .news_scraper import NewsScraper
import numpy as np
from typing import Dict, Any
import sys
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)
# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class Processor(ABC):
    @abstractmethod
    def process(self, data):
        pass

class StockInfoProcessor(Processor):
    def process(self, data):
        """
        Extract key information for stock analysis from the given data.
        
        :param data: Dictionary containing raw stock data
        :return: Dictionary with extracted key information
        """
        stock_info = {
            # Company Information
            "symbol": data.get("symbol"),
            "company_name": data.get("longName"),
            "industry": data.get("industry"),
            "sector": data.get("sector"),
            "website": data.get("website"),
            "employees": data.get("fullTimeEmployees"),
            
            # Financial Metrics
            "market_cap": data.get("marketCap"),
            "enterprise_value": data.get("enterpriseValue"),
            "revenue": data.get("totalRevenue"),
            "ebitda": data.get("ebitda"),
            "net_income": data.get("netIncomeToCommon"),
            "eps": data.get("trailingEps"),
            "forward_eps": data.get("forwardEps"),
            
            # Valuation Ratios
            "pe_ratio": data.get("trailingPE"),
            "forward_pe": data.get("forwardPE"),
            "peg_ratio": data.get("pegRatio"),
            "price_to_sales": data.get("priceToSalesTrailing12Months"),
            "price_to_book": data.get("priceToBook"),
            "enterprise_to_revenue": data.get("enterpriseToRevenue"),
            "enterprise_to_ebitda": data.get("enterpriseToEbitda"),
            
            # Dividends
            "dividend_rate": data.get("dividendRate"),
            "dividend_yield": data.get("dividendYield"),
            "payout_ratio": data.get("payoutRatio"),
            
            # Growth and Performance
            "revenue_growth": data.get("revenueGrowth"),
            "earnings_growth": data.get("earningsGrowth"),
            "return_on_assets": data.get("returnOnAssets"),
            "return_on_equity": data.get("returnOnEquity"),
            
            # Stock Price Information
            "current_price": data.get("currentPrice"),
            "52_week_low": data.get("fiftyTwoWeekLow"),
            "52_week_high": data.get("fiftyTwoWeekHigh"),
            "50_day_average": data.get("fiftyDayAverage"),
            "200_day_average": data.get("twoHundredDayAverage"),
            
            # Trading Information
            "average_volume": data.get("averageVolume"),
            "shares_outstanding": data.get("sharesOutstanding"),
            "float_shares": data.get("floatShares"),
            "beta": data.get("beta"),
            
            # Analyst Recommendations
            "target_low_price": data.get("targetLowPrice"),
            "target_median_price": data.get("targetMedianPrice"),
            "target_mean_price": data.get("targetMeanPrice"),
            "target_high_price": data.get("targetHighPrice"),
            "recommendation": data.get("recommendationKey"),
            
            # Financial Health
            "total_cash": data.get("totalCash"),
            "total_debt": data.get("totalDebt"),
            "debt_to_equity": data.get("debtToEquity"),
            "current_ratio": data.get("currentRatio"),
            "quick_ratio": data.get("quickRatio"),
            
            # Profitability
            "gross_margins": data.get("grossMargins"),
            "operating_margins": data.get("operatingMargins"),
            "profit_margins": data.get("profitMargins"),
            
            # Cash Flow
            "operating_cash_flow": data.get("operatingCashflow"),
            "free_cash_flow": data.get("freeCashflow"),
            
            # Risk Metrics
            "overall_risk": data.get("overallRisk"),
            "audit_risk": data.get("auditRisk"),
            "board_risk": data.get("boardRisk"),
            "compensation_risk": data.get("compensationRisk"),
            "shareholder_rights_risk": data.get("shareHolderRightsRisk"),
        }
        
        # Remove None values
        stock_info = {k: v for k, v in stock_info.items() if v is not None}
        
        return stock_info


class NewsProcessor(Processor):

    def process(self, ticker):
        """
        Extract key information for news articles from the given data.
        
        :param data: List of dictionaries containing raw news data
        :return: List of dictionaries with extracted key information
        """
        news_scraper = NewsScraper()
        news_data = news_scraper.scrape_and_collect(ticker)
        news_analyzer = NewsAnalyzer()
        dct = {}
        title_url_sentiment = {}
        counter = 0
        for key, value in news_data.items():
            title = key[0]
            url = key[1]

            sentiment = news_analyzer.analyze_news_article(value, ticker, counter)
            counter +=1
            print(counter)
            print(sentiment)
            if sentiment:
                dct[f"Article {counter}:"] = sentiment
                title_url_sentiment[title, url] = sentiment
    
        result = news_analyzer.conclusion(dct, ticker)
        return result, title_url_sentiment
        
class StockHistoryProcessor(Processor):
    def __init__(self):
        """
        Initialize the StockHistoryProcessor with a DataFrame of stock history.
        
        :param df: DataFrame containing stock data with columns: Date, Open, High, Low, Close, Volume
        """
        self.df = ""
        self.metrics = {}

    def calculate_key_metrics(self) -> None:
        """Calculate key metrics and indicators from the stock data."""
        # Basic price information
        self.metrics['latest_price'] = self.df['Close'].iloc[-1]
        self.metrics['price_change'] = self.df['Close'].iloc[-1] - self.df['Close'].iloc[0]
        self.metrics['price_change_percent'] = (self.metrics['price_change'] / self.df['Close'].iloc[0]) * 100

        # Returns
        self.df['Daily_Return'] = self.df['Close'].pct_change()
        self.metrics['total_return'] = (self.df['Close'].iloc[-1] / self.df['Close'].iloc[0] - 1) * 100
        self.metrics['annualized_return'] = ((1 + self.metrics['total_return'] / 100) ** (252 / len(self.df)) - 1) * 100

        # Volatility
        self.metrics['volatility'] = self.df['Daily_Return'].std() * np.sqrt(252) * 100

        # Moving Averages
        self.metrics['SMA_5'] = self.df['Close'].rolling(window=5).mean().iloc[-1]
        self.metrics['SMA_10'] = self.df['Close'].rolling(window=10).mean().iloc[-1]
        self.metrics['SMA_20'] = self.df['Close'].rolling(window=20).mean().iloc[-1]
        self.metrics['SMA_50'] = self.df['Close'].rolling(window=50).mean().iloc[-1]
        self.metrics['SMA_200'] = self.df['Close'].rolling(window=200).mean().iloc[-1]

        # Relative Strength Index (RSI)
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.metrics['RSI'] = 100 - (100 / (1 + rs.iloc[-1]))

        # Bollinger Bands
        rolling_mean = self.df['Close'].rolling(window=20).mean()
        rolling_std = self.df['Close'].rolling(window=20).std()
        self.metrics['upper_bollinger'] = rolling_mean.iloc[-1] + (rolling_std.iloc[-1] * 2)
        self.metrics['lower_bollinger'] = rolling_mean.iloc[-1] - (rolling_std.iloc[-1] * 2)

        # Volume analysis
        self.metrics['average_volume'] = self.df['Volume'].mean()
        self.metrics['volume_change'] = (self.df['Volume'].iloc[-1] / self.metrics['average_volume'] - 1) * 100

        # High and Low
        self.metrics['52_week_high'] = self.df['High'].rolling(window=self.df.shape[0]).max().iloc[-1]
        self.metrics['52_week_low'] = self.df['Low'].rolling(window=self.df.shape[0]).min().iloc[-1]

        # Sharpe Ratio (assuming risk-free rate of 2%)
        risk_free_rate = 0.02
        excess_returns = self.df['Daily_Return'] - risk_free_rate / 252
        self.metrics['sharpe_ratio'] = np.sqrt(252) * excess_returns.mean() / excess_returns.std()

        # Maximum Drawdown
        cumulative_returns = (1 + self.df['Daily_Return']).cumprod()
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns / peak - 1)
        self.metrics['max_drawdown'] = drawdown.min() * 100

    def get_metrics_dict(self) -> Dict[str, Any]:
        """
        Return the calculated metrics as a dictionary.
        
        :return: Dictionary of calculated metrics
        """
        return self.metrics
    
    def preprocess(self, df):
        # Implement stock history processing logic here
        self.df = df
        self.calculate_key_metrics()
        results = self.get_metrics_dict()
        print(results)
        return results

    def process(self, results):
        # Implement stock history processing logic here

        prompt = f"""You are an experienced stock analyst with deep knowledge of technical and fundamental analysis. Your task is to analyze the following stock data and provide a comprehensive analysis report, in a step-by-step, chain-of-thought manner. Consider various aspects such as price movements, technical indicators, volatility, and performance metrics. Explain your reasoning for each observation and conclusion. Additionally,  provide your recommendation on whether to buy, sell, or hold the stock based on the analysis and give top 5 reasons why.
        Stock Data:{results}
        """
        response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.5,
        max_tokens=500,
    )
        reply = response.choices[0].message.content

        prompt = f"""As an expert stock analyst, analyze the following comprehensive stock report and provide a recommendation in JSON format. Your analysis should include a rating (buy, sell, or hold) and five key reasons supporting your recommendation. Format your response as a valid JSON object with the following structure:

        {{
        "Rating": "Buy|Sell|Hold",
        "Reason 1": "First key reason for the recommendation",
        "Reason 2": "Second key reason for the recommendation",
        "Reason 3": "Third key reason for the recommendation",
        "Reason 4": "Fourth key reason for the recommendation",
        "Reason 5": "Fifth key reason for the recommendation"
        }}

        Ensure that your analysis considers all aspects of the report, including:

            Price movements and performance metrics
            Technical indicators (SMAs, RSI, Bollinger Bands)
            Volatility
            Volume analysis
            Performance metrics (Sharpe Ratio, Max Drawdown)

        Provide concise, clear reasons that directly support your rating. Each reason should be a complete sentence and should not exceed 200 characters.

        Here's the comprehensive stock analysis report for your review:

        {reply}

        Based on this report, provide your recommendation and reasoning in the specified JSON format."""
        response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.5,
        max_tokens=500,
        response_format = { "type": "json_object" }
    )
        return response.choices[0].message.content 

##template for other processors
class OtherDataProcessor(Processor):
    def process(self, data):
        # Implement other data processing logic here
        pass

# Factory class to create different types of processors
class ProcessorFactory:
    @staticmethod
    def get_processor(processor_type):
        if processor_type == "stock_info":
            return StockInfoProcessor()
        ##todo: add other processors here
        elif processor_type == "news":
            return NewsProcessor()
        elif processor_type == "stock_history":
            return StockHistoryProcessor()
        elif processor_type == "other_data":
            return OtherDataProcessor()
        else:
            raise ValueError(f"Unknown processor type: {processor_type}")


