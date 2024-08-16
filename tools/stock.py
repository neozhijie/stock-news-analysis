import yfinance as yf
from typing import Optional, List, Dict, Any

class Stock:
    def __init__(self, ticker: str):
        self.ticker = yf.Ticker(ticker)

    def get_info(self) -> Dict[str, Any]:
        """Get all stock info."""
        return self.ticker.info

    def get_history(self, period: str = "1y"):
        """Get historical market data."""
        return self.ticker.history(period=period)
    
    def get_full_history(self, period: str = "max"):
        """Get historical market data for max period."""
        return self.ticker.history(period=period, interval="1d")

    def get_quarterly_income_statement(self):
        """Show quarterly income statement."""
        return self.ticker.quarterly_income_stmt

    def get_quarterly_balance_sheet(self):
        """Show quarterly balance sheet."""
        return self.ticker.quarterly_balance_sheet

    def get_quarterly_cashflow(self):
        """Show quarterly cash flow statement."""
        return self.ticker.quarterly_cashflow

    def get_insider_transactions(self):
        """Show insider transactions."""
        return self.ticker.insider_transactions
    
    def get_all_data(self) -> Dict[str, Any]:
        """
        Get all available data for the stock as a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary containing all the stock data.
        """
        all_data = {
            "info": self.get_info(),
            "history": self.get_history(),
            "quarterly_income_statement": self.get_quarterly_income_statement().to_dict(),
            "quarterly_balance_sheet": self.get_quarterly_balance_sheet().to_dict(),
            "quarterly_cashflow": self.get_quarterly_cashflow().to_dict(),
            "insider_transactions": self.get_insider_transactions().to_dict(),
        }
        return all_data
